# Avance del comprador para el sprint 2

## Funcionalidades disponibles

- `Mis pedidos`: consulta de las reservas del comprador autenticado, ordenadas desde la más reciente.
- Filtro por los estados pendiente, en preparación, listo para retirar y entregado.
- Detalle del pedido con productos, cantidades, subtotales, total, puesto y punto de retiro.
- Restricción de acceso: los compradores no pueden consultar pedidos ajenos y los vendedores no pueden entrar a estas vistas de comprador.
- Enlaces desde el menú, el panel de compras y la confirmación de una reserva.
- Confirmación que conserva los centavos del total y permite volver a consultar la reserva después de recargar el catálogo.
- Ajustes para celular en navegación, catálogo, formularios, confirmación y consulta de pedidos. La tabla `Mis productos` se desplaza dentro de su contenedor.

## Relación con las tareas propuestas

| Tarea | Avance |
|---|---|
| S2-03: selector de horario | Pendiente de la integración del modelo y las franjas disponibles. |
| S2-05: confirmación y mensajes | Avance sobre la reserva actual: resumen, total con centavos y acceso al detalle. Falta el horario de retiro. |
| S2-13: Mis pedidos | Implementada la consulta, la interfaz, el detalle, los filtros y la protección de pedidos propios. Se incluyó la consulta mínima para poder ejecutar este avance sin esperar otra rama. |
| S2-17: adaptación móvil | Implementada sobre las pantallas existentes y las nuevas vistas del comprador. Las futuras pantallas deberán verificarse al integrarlas. |

El estado `en_preparacion` se incorporó al modelo y tiene su migración. El cambio de estados desde la interfaz del vendedor corresponde a la gestión de pedidos pendiente.

## Conceptos utilizados de los auxiliares

| Material | Aplicación en este avance |
|---|---|
| Auxiliar 1: Django | Modelos, migraciones, rutas y templates que recorren resultados de una consulta. |
| Auxiliar 2: Usuarios | Filtrar los registros por el usuario autenticado, como en la lista de tareas propia del ejemplo. |
| Auxiliar 3: HTML y CSS | Herencia de templates, hoja de estilos local y adaptación de las pantallas con CSS. |
| Auxiliar 4: Forms | `forms.Form`, `ChoiceField`, validación mediante `is_valid()` y lectura de `cleaned_data` para el filtro de estado. |

Se mantuvo el estilo de vistas de clase y mixins que ya usa el repositorio. `ListView` entrega la lista y `DetailView` obtiene un pedido desde la consulta restringida al comprador. `prefetch_related` permite cargar los productos y vendedores relacionados sin consultar la base de datos por cada fila.

## Comprobación manual

1. Iniciar sesión con una cuenta compradora.
2. Reservar un producto desde el catálogo y abrir el enlace al detalle en la confirmación.
3. Entrar a `Mis pedidos` y comprobar que la reserva aparece con su estado y total.
4. Filtrar por estado y volver a mostrar todos los pedidos.
5. Entrar con otro comprador y comprobar que el pedido anterior no aparece. Su URL de detalle debe responder con página no encontrada.
6. Revisar catálogo, confirmación, listado y detalle en escritorio y celular.

Los distintos estados se pueden comprobar con datos de prueba mientras se integra la gestión del vendedor. La vista muestra el estado registrado al cargar la página.

## Integración pendiente

Las franjas de retiro y su selector requieren los cambios de horarios. Al integrarlos, se agregará el horario a la reserva, la confirmación y la consulta de pedidos. La gestión del vendedor deberá utilizar los estados definidos en `Pedido.ESTADOS`.

## Correcciones de integridad

Cada detalle guarda `precio_unitario` al crear el pedido. El subtotal usa ese precio, por lo que editar el precio del producto no modifica compras anteriores. La migración conserva los pedidos existentes y les asigna el precio disponible al migrar; los precios originales que no se guardaron antes no pueden reconstruirse.

Al crear un `DetallePedido`, también se debe entregar `precio_unitario=producto.precio`. El detalle del comprador muestra este valor.

El descuento de stock utiliza `filter(...).update(stock=F("stock") - cantidad)` dentro de `transaction.atomic()`. La condición exige stock suficiente y disponibilidad en el momento de actualizar. Si otra petición ya reservó la última unidad, la segunda no crea un pedido. Si falla el guardado del detalle, se revierte también el descuento.

`CrearPedidoForm` valida el identificador y la cantidad antes de consultar el producto. `FiltroCatalogoForm` valida la categoría y el vendedor antes de filtrar. Ambos usan `IntegerField`, `is_valid()` y `cleaned_data`, siguiendo el enfoque del auxiliar de Forms. Los valores inválidos muestran mensajes y el catálogo permite limpiar sus filtros.
