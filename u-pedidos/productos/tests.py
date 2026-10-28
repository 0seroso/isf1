from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from usuarios.models import Usuario
from .models import Categoria, Producto, Vendedor


class CatalogoFiltrosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.comprador = Usuario.objects.create_user(username="comprador_catalogo", rol="comprador")
        cls.vendedor = Vendedor.objects.create(nombre="Puesto de prueba")
        cls.otro_vendedor = Vendedor.objects.create(nombre="Otro puesto")
        cls.categoria = Categoria.objects.create(nombre="Vegetariano")
        cls.producto = Producto.objects.create(
            vendedor=cls.vendedor, nombre="Almuerzo", precio=3000, stock=5
        )
        cls.producto.categorias.add(cls.categoria)
        cls.otro_producto = Producto.objects.create(
            vendedor=cls.otro_vendedor, nombre="Otro almuerzo", precio=4000, stock=5
        )
        Producto.objects.create(
            vendedor=cls.vendedor, nombre="No disponible", precio=3000, stock=5, disponible=False
        )
        cls.url = reverse("productos:catalogo")

    def setUp(self):
        self.client.force_login(self.comprador)

    def test_catalogo_sin_filtros_muestra_solo_productos_disponibles(self):
        response = self.client.get(self.url)

        self.assertEqual(set(response.context["productos"]), {self.producto, self.otro_producto})

    def test_filtra_por_categoria_y_vendedor_y_conserva_la_seleccion(self):
        response = self.client.get(
            self.url, {"categoria": self.categoria.pk, "vendedor": self.vendedor.pk}
        )

        self.assertEqual(list(response.context["productos"]), [self.producto])
        self.assertEqual(response.context["categoria_actual"], self.categoria.pk)
        self.assertEqual(response.context["vendedor_actual"], self.vendedor.pk)

    def test_filtros_invalidos_muestran_error_y_permiten_limpiar_la_busqueda(self):
        for campo in ["categoria", "vendedor"]:
            for valor in ["abc", "²", "-1", "0", "1.5", "9" * 5000]:
                with self.subTest(campo=campo, valor=valor[:20]):
                    response = self.client.get(self.url, {campo: valor})
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, "Los filtros recibidos no son válidos")
                    self.assertContains(response, "Limpiar filtros")
                    self.assertEqual(list(response.context["productos"]), [])

    def test_filtros_vacios_equivalen_a_mostrar_todos(self):
        response = self.client.get(self.url, {"categoria": "", "vendedor": ""})

        self.assertEqual(set(response.context["productos"]), {self.producto, self.otro_producto})

    def test_categoria_inexistente_devuelve_catalogo_vacio(self):
        response = self.client.get(self.url, {"categoria": 999999})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["productos"]), [])


class ProductoPrecioTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(username="vendedor_precios", rol="vendedor")
        cls.vendedor = Vendedor.objects.create(usuario=cls.usuario, nombre="Puesto de precios")
        cls.url = reverse("productos:producto_nuevo")

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_vendedor_puede_publicar_un_precio_con_centavos(self):
        response = self.client.post(
            self.url,
            {"nombre": "Almuerzo", "precio": "3000.50", "stock": "5", "disponible": "on"},
        )

        self.assertRedirects(response, reverse("productos:mis_productos"))
        producto = Producto.objects.get()
        self.assertEqual(producto.precio, Decimal("3000.50"))
        self.assertEqual(producto.vendedor, self.vendedor)

    def test_admite_el_precio_positivo_minimo_de_un_centavo(self):
        response = self.client.post(
            self.url,
            {"nombre": "Producto", "precio": "0.01", "stock": "1", "disponible": "on"},
        )

        self.assertRedirects(response, reverse("productos:mis_productos"))
        self.assertEqual(Producto.objects.get().precio, Decimal("0.01"))

    def test_rechaza_precios_no_positivos_o_con_mas_de_dos_decimales(self):
        for precio in ["0", "-1", "3000.501"]:
            with self.subTest(precio=precio):
                response = self.client.post(
                    self.url,
                    {"nombre": "Almuerzo", "precio": precio, "stock": "5", "disponible": "on"},
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("precio", response.context["form"].errors)
                self.assertEqual(Producto.objects.count(), 0)
