from decimal import Decimal

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class PrecioUnitarioMigrationTests(TransactionTestCase):
    def test_migracion_conserva_pedidos_existentes_y_fija_su_precio(self):
        executor = MigrationExecutor(connection)
        destinos_actuales = executor.loader.graph.leaf_nodes()
        self.addCleanup(self.restaurar_migraciones, destinos_actuales)
        origen = [("pedidos", "0003_agregar_estado_en_preparacion")]
        executor.migrate(origen)
        modelos_anteriores = executor.loader.project_state(origen).apps
        Usuario = modelos_anteriores.get_model("usuarios", "Usuario")
        Vendedor = modelos_anteriores.get_model("productos", "Vendedor")
        Producto = modelos_anteriores.get_model("productos", "Producto")
        Pedido = modelos_anteriores.get_model("pedidos", "Pedido")
        DetallePedido = modelos_anteriores.get_model("pedidos", "DetallePedido")

        comprador = Usuario.objects.create(username="comprador_anterior", rol="comprador")
        vendedor = Vendedor.objects.create(nombre="Puesto anterior")
        producto = Producto.objects.create(
            vendedor=vendedor, nombre="Producto anterior", precio=Decimal("3000.50"), stock=5
        )
        pedido = Pedido.objects.create(comprador=comprador, estado="listo")
        detalle = DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=2)

        destino = [("pedidos", "0004_guardar_precio_unitario")]
        executor = MigrationExecutor(connection)
        executor.migrate(destino)
        modelos_nuevos = executor.loader.project_state(destino).apps
        DetalleNuevo = modelos_nuevos.get_model("pedidos", "DetallePedido")
        PedidoNuevo = modelos_nuevos.get_model("pedidos", "Pedido")
        ProductoNuevo = modelos_nuevos.get_model("productos", "Producto")
        detalle_migrado = DetalleNuevo.objects.get(pk=detalle.pk)

        self.assertEqual(detalle_migrado.precio_unitario, Decimal("3000.50"))
        self.assertEqual(detalle_migrado.cantidad, 2)
        self.assertEqual(detalle_migrado.pedido_id, pedido.pk)
        self.assertEqual(PedidoNuevo.objects.get(pk=pedido.pk).estado, "listo")
        ProductoNuevo.objects.filter(pk=producto.pk).update(precio=Decimal("5000.00"))
        detalle_migrado.refresh_from_db()
        self.assertEqual(detalle_migrado.precio_unitario, Decimal("3000.50"))

    def restaurar_migraciones(self, destinos):
        MigrationExecutor(connection).migrate(destinos)


class RetiroMigrationTests(TransactionTestCase):
    def test_migracion_de_retiro_conserva_pedidos_y_precios_anteriores(self):
        executor = MigrationExecutor(connection)
        destinos_actuales = executor.loader.graph.leaf_nodes()
        self.addCleanup(self.restaurar_migraciones, destinos_actuales)
        origen = [("pedidos", "0004_guardar_precio_unitario")]
        executor.migrate(origen)
        anteriores = executor.loader.project_state(origen).apps
        Usuario = anteriores.get_model("usuarios", "Usuario")
        Vendedor = anteriores.get_model("productos", "Vendedor")
        Producto = anteriores.get_model("productos", "Producto")
        Pedido = anteriores.get_model("pedidos", "Pedido")
        DetallePedido = anteriores.get_model("pedidos", "DetallePedido")
        comprador = Usuario.objects.create(username="comprador_sin_franja", rol="comprador")
        vendedor = Vendedor.objects.create(nombre="Puesto sin franjas")
        producto = Producto.objects.create(
            vendedor=vendedor, nombre="Producto anterior", precio=Decimal("5000.00"), stock=5
        )
        pedido = Pedido.objects.create(comprador=comprador, estado="en_preparacion")
        detalle = DetallePedido.objects.create(
            pedido=pedido, producto=producto, cantidad=2, precio_unitario=Decimal("3000.50")
        )

        destino = [("pedidos", "0005_pedido_retiro_inicio")]
        executor = MigrationExecutor(connection)
        executor.migrate(destino)
        nuevos = executor.loader.project_state(destino).apps
        PedidoNuevo = nuevos.get_model("pedidos", "Pedido")
        DetalleNuevo = nuevos.get_model("pedidos", "DetallePedido")

        pedido_migrado = PedidoNuevo.objects.get(pk=pedido.pk)
        detalle_migrado = DetalleNuevo.objects.get(pk=detalle.pk)
        self.assertIsNone(pedido_migrado.retiro_inicio)
        self.assertEqual(pedido_migrado.comprador_id, comprador.pk)
        self.assertEqual(pedido_migrado.estado, "en_preparacion")
        self.assertEqual(detalle_migrado.precio_unitario, Decimal("3000.50"))
        self.assertEqual(detalle_migrado.cantidad, 2)

    def restaurar_migraciones(self, destinos):
        MigrationExecutor(connection).migrate(destinos)
