from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from pedidos.models import DetallePedido, Pedido
from productos.models import Producto, Vendedor
from usuarios.models import Usuario


AHORA = datetime(2026, 10, 9, 12, 0, tzinfo=ZoneInfo("America/Santiago"))
RETIRO = "13:30"


class CrearPedidoViewTests(TestCase):
    def setUp(self):
        reloj = patch("django.utils.timezone.now", return_value=AHORA)
        reloj.start()
        self.addCleanup(reloj.stop)

    @classmethod
    def setUpTestData(cls):
        # Crear vendedor y producto
        cls.vendedor_user = Usuario.objects.create_user(
            username="vendedor_test",
            password="password123",
            rol="vendedor",
        )
        cls.vendedor = Vendedor.objects.create(
            usuario=cls.vendedor_user,
            nombre="Puesto Test",
            ubicacion="Patio Central",
        )
        cls.producto = Producto.objects.create(
            vendedor=cls.vendedor,
            nombre="Sandwich Ave Palta",
            descripcion="Sandwich fresco",
            precio=3000,
            stock=10,
            disponible=True,
        )

        # Crear comprador
        cls.comprador = Usuario.objects.create_user(
            username="comprador_test",
            password="password123",
            rol="comprador",
        )
        cls.crear_url = reverse("pedidos:crear_pedido")

    def test_comprador_puede_crear_pedido_exitosamente(self):
        self.client.login(username="comprador_test", password="password123")
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "3", "retiro": RETIRO},
        )

        self.assertRedirects(response, reverse("productos:catalogo"))
        self.assertEqual(Pedido.objects.count(), 1)
        pedido = Pedido.objects.first()
        self.assertEqual(pedido.comprador, self.comprador)
        self.assertEqual(pedido.estado, "pendiente")

        self.assertEqual(DetallePedido.objects.count(), 1)
        detalle = DetallePedido.objects.first()
        self.assertEqual(detalle.pedido, pedido)
        self.assertEqual(detalle.producto, self.producto)
        self.assertEqual(detalle.cantidad, 3)
        self.assertEqual(detalle.precio_unitario, Decimal("3000.00"))
        self.assertEqual(pedido.total(), 9000)

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 7)
        self.assertTrue(self.producto.disponible)

    def test_crear_pedido_muestra_resumen_y_punto_de_retiro(self):
        self.client.login(username="comprador_test", password="password123")
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "2", "retiro": RETIRO},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "confirmada con éxito")
        self.assertContains(response, "Punto de retiro:")
        self.assertContains(response, "Patio Central")
        self.assertContains(response, "Puesto Test")
        self.assertContains(response, "2x Sandwich Ave Palta")
        self.assertContains(response, "$6.000")

    def test_confirmacion_muestra_pesos_enteros_y_permite_abrir_el_detalle(self):
        self.producto.precio = Decimal("3000.00")
        self.producto.save(update_fields=["precio"])
        self.client.force_login(self.comprador)

        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.pk, "cantidad": "3", "retiro": RETIRO},
        )

        pedido = Pedido.objects.get(comprador=self.comprador)
        self.assertEqual(self.client.session["reserva_confirmada"]["total"], "9000.00")
        confirmacion = self.client.get(response.url)
        detalle_url = reverse("pedidos:detalle_pedido", args=[pedido.pk])
        self.assertContains(confirmacion, "$9.000")
        self.assertContains(confirmacion, detalle_url)
        self.assertContains(confirmacion, reverse("pedidos:mis_pedidos"))
        detalle = self.client.get(detalle_url)
        self.assertEqual(detalle.status_code, 200)
        self.assertContains(detalle, "$9.000")
        # Al recargar el catálogo la confirmación desaparece, pero el pedido persiste.
        catalogo = self.client.get(reverse("productos:catalogo"))
        self.assertNotContains(catalogo, 'id="titulo-confirmacion"')
        self.assertContains(self.client.get(detalle_url), "$9.000")

    def test_crear_pedido_agota_stock_marca_no_disponible(self):
        self.client.login(username="comprador_test", password="password123")
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "10", "retiro": RETIRO},
        )

        self.assertRedirects(response, reverse("productos:catalogo"))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 0)
        self.assertFalse(self.producto.disponible)

    def test_no_permite_pedir_mas_que_el_stock_disponible(self):
        self.client.login(username="comprador_test", password="password123")
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "11", "retiro": RETIRO},
        )

        self.assertRedirects(response, reverse("productos:catalogo"))
        self.assertEqual(Pedido.objects.count(), 0)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)

        mensajes = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("No hay suficiente stock" in m for m in mensajes))

    def test_dos_lecturas_de_la_ultima_unidad_no_crean_dos_reservas(self):
        self.producto.stock = 1
        self.producto.save(update_fields=["stock"])
        lectura_anterior = Producto.objects.get(pk=self.producto.pk)
        self.client.force_login(self.comprador)
        datos = {"producto_id": self.producto.pk, "cantidad": "1", "retiro": RETIRO}
        self.client.post(self.crear_url, datos)

        # Simula otra petición que leyó la misma unidad antes de la primera compra.
        with patch("pedidos.views.get_object_or_404", return_value=lectura_anterior):
            response = self.client.post(self.crear_url, datos)

        self.assertRedirects(response, reverse("productos:catalogo"))
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(DetallePedido.objects.count(), 1)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 0)
        self.assertFalse(self.producto.disponible)

    def test_reserva_no_sobrescribe_cambios_recientes_del_producto(self):
        lectura_anterior = Producto.objects.get(pk=self.producto.pk)
        Producto.objects.filter(pk=self.producto.pk).update(
            nombre="Nombre actualizado", precio=Decimal("3500.00"), stock=8
        )
        self.client.force_login(self.comprador)

        with patch("pedidos.views.get_object_or_404", return_value=lectura_anterior):
            self.client.post(self.crear_url, {"producto_id": self.producto.pk, "cantidad": "2", "retiro": RETIRO})

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, "Nombre actualizado")
        self.assertEqual(self.producto.precio, Decimal("3500.00"))
        self.assertEqual(self.producto.stock, 6)
        self.assertEqual(Pedido.objects.get().total(), Decimal("7000.00"))

    def test_cambiar_el_precio_del_producto_no_modifica_pedidos_anteriores(self):
        self.client.force_login(self.comprador)
        datos = {"producto_id": self.producto.pk, "cantidad": "2", "retiro": RETIRO}
        self.client.post(self.crear_url, datos)
        pedido_anterior = Pedido.objects.get()
        Producto.objects.filter(pk=self.producto.pk).update(precio=Decimal("5000.00"))

        self.client.post(self.crear_url, datos)

        pedido_anterior.refresh_from_db()
        pedido_nuevo = Pedido.objects.exclude(pk=pedido_anterior.pk).get()
        self.assertEqual(pedido_anterior.total(), Decimal("6000.00"))
        self.assertEqual(pedido_nuevo.total(), Decimal("10000.00"))
        self.assertEqual(pedido_anterior.items.get().precio_unitario, Decimal("3000.00"))
        response = self.client.get(reverse("pedidos:detalle_pedido", args=[pedido_anterior.pk]))
        self.assertContains(response, "$6.000")
        self.assertNotContains(response, "$10.000")

    def test_fallo_al_guardar_detalle_revierte_pedido_y_descuento_de_stock(self):
        self.client.force_login(self.comprador)

        with patch("pedidos.views.DetallePedido.objects.create", side_effect=RuntimeError("Fallo de prueba")):
            with self.assertRaises(RuntimeError):
                self.client.post(self.crear_url, {"producto_id": self.producto.pk, "cantidad": "2", "retiro": RETIRO})

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)
        self.assertTrue(self.producto.disponible)
        self.assertEqual(Pedido.objects.count(), 0)
        self.assertEqual(DetallePedido.objects.count(), 0)

    def test_no_permite_pedir_producto_no_disponible(self):
        self.producto.disponible = False
        self.producto.save()

        self.client.login(username="comprador_test", password="password123")
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "1", "retiro": RETIRO},
        )

        self.assertRedirects(response, reverse("productos:catalogo"))
        self.assertEqual(Pedido.objects.count(), 0)

        mensajes = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("no se encuentra disponible" in m for m in mensajes))

    def test_cantidad_invalida_no_crea_pedido(self):
        self.client.login(username="comprador_test", password="password123")
        for cantidad_invalida in ["0", "-2", "abc", ""]:
            response = self.client.post(
                self.crear_url,
                {"producto_id": self.producto.id, "cantidad": cantidad_invalida, "retiro": RETIRO},
            )
            self.assertRedirects(response, reverse("productos:catalogo"))
            self.assertEqual(Pedido.objects.count(), 0)

    def test_identificadores_invalidos_se_rechazan_sin_crear_pedidos(self):
        self.client.force_login(self.comprador)
        for identificador in ["abc", "²", "-1", "0", "1.5", "9" * 5000, ""]:
            with self.subTest(identificador=identificador[:20]):
                response = self.client.post(
                    self.crear_url, {"producto_id": identificador, "cantidad": "1", "retiro": RETIRO}
                )
                self.assertRedirects(response, reverse("productos:catalogo"))
                mensajes = [m.message for m in get_messages(response.wsgi_request)]
                self.assertIn("Selecciona un producto válido del catálogo.", mensajes)
                self.assertEqual(Pedido.objects.count(), 0)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)

    def test_identificador_valido_de_producto_inexistente_devuelve_404(self):
        self.client.force_login(self.comprador)

        response = self.client.post(self.crear_url, {"producto_id": 999999, "cantidad": "1", "retiro": RETIRO})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_cantidad_ausente_fraccionaria_o_desmesurada_se_rechaza(self):
        self.client.force_login(self.comprador)
        for cantidad in [None, "1.5", "9" * 5000]:
            with self.subTest(cantidad=str(cantidad)[:20]):
                datos = {"producto_id": self.producto.pk, "retiro": RETIRO}
                if cantidad is not None:
                    datos["cantidad"] = cantidad
                response = self.client.post(self.crear_url, datos)
                self.assertRedirects(response, reverse("productos:catalogo"))
                self.assertEqual(Pedido.objects.count(), 0)

    def test_vendedor_no_puede_crear_pedido(self):
        self.client.login(username="vendedor_test", password="password123")
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "1", "retiro": RETIRO},
        )

        self.assertRedirects(response, reverse("usuarios:dashboard"), target_status_code=302)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_usuario_anonimo_es_redirigido_a_login(self):
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "1", "retiro": RETIRO},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response.url)
        self.assertEqual(Pedido.objects.count(), 0)


class ConsultaPedidosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.comprador = Usuario.objects.create_user(username="comprador", rol="comprador")
        cls.otro_comprador = Usuario.objects.create_user(username="otro_comprador", rol="comprador")
        cls.vendedor_user = Usuario.objects.create_user(username="vendedor", rol="vendedor")
        cls.vendedor = Vendedor.objects.create(
            usuario=cls.vendedor_user,
            nombre="Puesto de prueba",
            ubicacion="Patio central",
        )
        cls.producto = Producto.objects.create(
            vendedor=cls.vendedor,
            nombre="Almuerzo de prueba",
            precio=Decimal("3200.00"),
            stock=10,
        )
        cls.pedido = Pedido.objects.create(comprador=cls.comprador)
        DetallePedido.objects.create(
            pedido=cls.pedido,
            producto=cls.producto,
            cantidad=2,
            precio_unitario=cls.producto.precio,
        )
        cls.pedido_ajeno = Pedido.objects.create(comprador=cls.otro_comprador)
        cls.pedido_sin_comprador = Pedido.objects.create()
        cls.lista_url = reverse("pedidos:mis_pedidos")

    def setUp(self):
        self.client.force_login(self.comprador)

    def test_lista_solo_incluye_pedidos_del_comprador_actual(self):
        response = self.client.get(self.lista_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["pedidos"]), [self.pedido])
        self.assertContains(response, "Almuerzo de prueba")
        self.assertContains(response, reverse("pedidos:detalle_pedido", args=[self.pedido.pk]))

    def test_lista_ordena_por_fecha_y_desempata_por_id(self):
        fecha = timezone.now() - timedelta(days=1)
        Pedido.objects.filter(pk=self.pedido.pk).update(fecha_creacion=fecha)
        segundo = Pedido.objects.create(comprador=self.comprador, fecha_creacion=fecha)
        reciente = Pedido.objects.create(comprador=self.comprador)

        response = self.client.get(self.lista_url)

        self.assertEqual(list(response.context["pedidos"]), [reciente, segundo, self.pedido])

    def test_filtro_muestra_solo_pedidos_propios_con_el_estado_elegido(self):
        listo = Pedido.objects.create(comprador=self.comprador, estado="listo")
        Pedido.objects.create(comprador=self.otro_comprador, estado="listo")

        response = self.client.get(self.lista_url, {"estado": "listo"})

        self.assertEqual(list(response.context["pedidos"]), [listo])
        self.assertContains(response, "Listo para retirar")

    def test_estado_invalido_muestra_error_y_no_devuelve_pedidos(self):
        response = self.client.get(self.lista_url, {"estado": "inexistente"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("estado", response.context["form_filtros"].errors)
        self.assertEqual(list(response.context["pedidos"]), [])

    def test_comprador_sin_pedidos_recibe_mensaje_y_acceso_al_catalogo(self):
        comprador_nuevo = Usuario.objects.create_user(username="sin_pedidos", rol="comprador")
        self.client.force_login(comprador_nuevo)

        response = self.client.get(self.lista_url)

        self.assertContains(response, "Aún no tienes pedidos")
        self.assertContains(response, reverse("productos:catalogo"))

    def test_filtro_sin_resultados_tiene_mensaje_especifico(self):
        response = self.client.get(self.lista_url, {"estado": "entregado"})

        self.assertContains(response, "No tienes pedidos con el estado seleccionado")

    def test_detalle_propio_muestra_productos_cantidades_total_y_retiro(self):
        response = self.client.get(reverse("pedidos:detalle_pedido", args=[self.pedido.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["pedido"].total(), Decimal("6400.00"))
        self.assertContains(response, "Almuerzo de prueba")
        self.assertContains(response, "Puesto de prueba")
        self.assertContains(response, "Patio central")
        self.assertContains(response, "$6.400")

    def test_no_se_pueden_consultar_pedidos_ajenos_ni_sin_comprador(self):
        for pedido in [self.pedido_ajeno, self.pedido_sin_comprador]:
            with self.subTest(pedido=pedido.pk):
                response = self.client.get(reverse("pedidos:detalle_pedido", args=[pedido.pk]))
                self.assertEqual(response.status_code, 404)

    def test_pedido_inexistente_devuelve_404(self):
        response = self.client.get(reverse("pedidos:detalle_pedido", args=[999999]))

        self.assertEqual(response.status_code, 404)

    def test_estado_en_preparacion_se_refleja_en_lista_y_detalle(self):
        self.pedido.estado = "en_preparacion"
        self.pedido.save(update_fields=["estado"])

        for url in [self.lista_url, reverse("pedidos:detalle_pedido", args=[self.pedido.pk])]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "En preparación")

    def test_horario_guardado_se_muestra_en_lista_y_detalle(self):
        self.pedido.retiro_inicio = datetime(2026, 10, 9, 13, 30, tzinfo=ZoneInfo("America/Santiago"))
        self.pedido.save(update_fields=["retiro_inicio"])

        for url in [self.lista_url, reverse("pedidos:detalle_pedido", args=[self.pedido.pk])]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "Horario de retiro:")
                self.assertContains(response, "09/10/2026 · 13:30–13:50")

    def test_pedido_anterior_sin_horario_se_puede_consultar(self):
        for url in [self.lista_url, reverse("pedidos:detalle_pedido", args=[self.pedido.pk])]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "Sin horario registrado")

    def test_pedido_sin_items_se_puede_consultar(self):
        pedido_vacio = Pedido.objects.create(comprador=self.comprador)

        response = self.client.get(reverse("pedidos:detalle_pedido", args=[pedido_vacio.pk]))

        self.assertContains(response, "Este pedido no tiene productos registrados")
        self.assertContains(response, "$0")

    def test_usuario_anonimo_debe_iniciar_sesion_para_lista_y_detalle(self):
        self.client.logout()

        for url in [self.lista_url, reverse("pedidos:detalle_pedido", args=[self.pedido.pk])]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("usuarios:login"), response.url)

    def test_vendedor_no_puede_acceder_a_lista_ni_detalle_de_comprador(self):
        self.client.force_login(self.vendedor_user)

        for url in [self.lista_url, reverse("pedidos:detalle_pedido", args=[self.pedido.pk])]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, reverse("usuarios:dashboard"), target_status_code=302)
