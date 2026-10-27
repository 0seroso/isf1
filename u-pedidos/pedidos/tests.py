from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from pedidos.models import DetallePedido, Pedido
from productos.models import Producto, Vendedor
from usuarios.models import Usuario


class CrearPedidoViewTests(TestCase):
    def setUp(self):
        # Crear vendedor y producto
        self.vendedor_user = Usuario.objects.create_user(
            username="vendedor_test",
            password="password123",
            rol="vendedor",
        )
        self.vendedor = Vendedor.objects.create(
            usuario=self.vendedor_user,
            nombre="Puesto Test",
            ubicacion="Patio Central",
        )
        self.producto = Producto.objects.create(
            vendedor=self.vendedor,
            nombre="Sandwich Ave Palta",
            descripcion="Sandwich fresco",
            precio=3000,
            stock=10,
            disponible=True,
        )

        # Crear comprador
        self.comprador = Usuario.objects.create_user(
            username="comprador_test",
            password="password123",
            rol="comprador",
        )
        self.crear_url = reverse("pedidos:crear_pedido")

    def test_comprador_puede_crear_pedido_exitosamente(self):
        self.client.login(username="comprador_test", password="password123")
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "3"},
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
        self.assertEqual(pedido.total(), 9000)

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 7)
        self.assertTrue(self.producto.disponible)

    def test_crear_pedido_muestra_resumen_y_punto_de_retiro(self):
        self.client.login(username="comprador_test", password="password123")
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "2"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "confirmada con éxito")
        self.assertContains(response, "Punto de retiro:")
        self.assertContains(response, "Patio Central")
        self.assertContains(response, "Puesto Test")
        self.assertContains(response, "2x Sandwich Ave Palta")
        self.assertContains(response, "$6000")

    def test_crear_pedido_agota_stock_marca_no_disponible(self):
        self.client.login(username="comprador_test", password="password123")
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "10"},
        )

        self.assertRedirects(response, reverse("productos:catalogo"))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 0)
        self.assertFalse(self.producto.disponible)

    def test_no_permite_pedir_mas_que_el_stock_disponible(self):
        self.client.login(username="comprador_test", password="password123")
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "11"},
        )

        self.assertRedirects(response, reverse("productos:catalogo"))
        self.assertEqual(Pedido.objects.count(), 0)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)

        mensajes = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("No hay suficiente stock" in m for m in mensajes))

    def test_no_permite_pedir_producto_no_disponible(self):
        self.producto.disponible = False
        self.producto.save()

        self.client.login(username="comprador_test", password="password123")
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "1"},
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
                {"producto_id": self.producto.id, "cantidad": cantidad_invalida},
            )
            self.assertRedirects(response, reverse("productos:catalogo"))
            self.assertEqual(Pedido.objects.count(), 0)

    def test_vendedor_no_puede_crear_pedido(self):
        self.client.login(username="vendedor_test", password="password123")
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "1"},
        )

        self.assertRedirects(response, reverse("usuarios:dashboard"), target_status_code=302)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_usuario_anonimo_es_redirigido_a_login(self):
        response = self.client.post(
            self.crear_url,
            {"producto_id": self.producto.id, "cantidad": "1"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response.url)
        self.assertEqual(Pedido.objects.count(), 0)
