# U-Pedidos

U-Pedidos es una aplicación web desarrollada para el curso **CC4401 – Ingeniería de Software** de la Universidad de Chile. Su objetivo es facilitar la coordinación entre personas que venden comida dentro de la comunidad universitaria y estudiantes que desean comprarla, centralizando la publicación de productos y la realización de pedidos anticipados.

**Equipo 2**

## Integrantes
- Ian Berdichewsky
- Benjamín Bolados
- Juan Pablo Carrasco
- Martín Friant
- Rodrigo Guerrero

## Problema que aborda
Actualmente, la información sobre los productos disponibles y los pedidos no se gestiona de forma centralizada, lo que dificulta que los estudiantes conozcan la oferta con anticipación y que los vendedores anticipen la demanda y organicen la preparación y entrega.

U-Pedidos busca centralizar este flujo en una aplicación web con dos roles principales: **comprador** y **vendedor**.

## Funcionalidades implementadas

### Comprador
- Registro e inicio de sesión con rol comprador.
- Acceso a un catálogo de productos disponibles.
- Visualización de nombre, precio, vendedor, categorías e imagen de los productos.
- Filtrado del catálogo por vendedor y categoría.
- Creación de pedidos indicando la cantidad solicitada.
- Validación para impedir pedidos con cantidades inválidas o superiores al stock disponible.
- Descuento automático del stock después de confirmar un pedido.
- Confirmación del pedido con información del producto, cantidad, total, vendedor y punto de retiro.
- Consulta de pedidos propios, ordenados desde el más reciente, con filtro por estado.
- Detalle de cada pedido con sus productos, cantidades, total, vendedor y punto de retiro.

### Vendedor
- Registro e inicio de sesión con rol vendedor.
- Creación de un perfil de vendedor con nombre y ubicación del puesto.
- Publicación de nuevos productos.
- Asociación automática de cada producto con el vendedor autenticado.
- Vista `Mis productos` con acceso únicamente a los productos propios.
- Edición y eliminación de productos propios.
- Actualización de stock y disponibilidad.

### Control de acceso
- Las funcionalidades se restringen de acuerdo con el rol de la cuenta.
- Una cuenta compradora no puede acceder a las funcionalidades exclusivas del vendedor.
- Una cuenta vendedora no puede realizar pedidos como comprador.

## Estado del Sprint 1
En la versión actualmente integrada del repositorio se encuentran implementadas las funcionalidades correspondientes al catálogo, publicación y actualización de productos y creación básica de pedidos con control de stock.

## Avance del Sprint 2
La consulta `Mis pedidos` y el detalle están disponibles para compradores autenticados. Cada comprador solo puede consultar sus propios pedidos. Los estados contemplados son pendiente, en preparación, listo para retirar y entregado.

La confirmación permite abrir el detalle de la reserva y conserva los centavos del total. El catálogo, la navegación y la consulta de pedidos se adaptan a pantallas pequeñas; la tabla de productos del vendedor permite desplazamiento horizontal dentro de su contenedor.

Quedan pendientes la integración de las franjas y el selector de horario de retiro, y la gestión de cambios de estado desde el panel del vendedor. El detalle de las tareas y los conceptos de los auxiliares utilizados está en [Avance del comprador](docs/avance-sprint-2-comprador.md).

## Tecnologías utilizadas

- Python
- Django **6.1.1**
- SQLite
- HTML
- CSS

## Instrucciones de ejecución

1. Clonar el repositorio

```bash
git clone https://github.com/DCC-CC4401/2026-2-CC4401-grupo-2.git
cd 2026-2-CC4401-grupo-2
```
2. Para levantar el proyecto localmente, ejecuta los siguientes comandos:

```bash
cd u-pedidos
python -m venv .venv
```

 3. Activa el entorno virtual según tu sistema operativo:

- En **Windows PowerShell**:

```powershell
.\.venv\Scripts\Activate.ps1
```

- En **Linux/macOS**:

```bash
source .venv/bin/activate
```

4. Instala las dependencias, aplica las migraciones y levanta el servidor:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata categorias
python manage.py runserver
```

El sitio quedará disponible en `http://127.0.0.1:8000/`.

## Estructura principal del proyecto

```text
2026-2-CC4401-grupo-2/
├── README.md
└── u-pedidos/
    ├── manage.py
    ├── requirements.txt
    ├── .gitignore
    ├── upedidos_project/   # Configuración principal del proyecto Django
    ├── usuarios/           # Registro, autenticación, perfiles y roles
    ├── productos/          # Productos, categorías, catálogo y gestión de oferta
    ├── pedidos/            # Pedidos, detalles y lógica de creación de pedidos
    ├── templates/          # Templates compartidos y autenticación
    └── static/             # Archivos estáticos del proyecto
```

Las aplicaciones principales son:

- `usuarios/`: registro, autenticación, perfiles y control de roles.
- `productos/`: productos, categorías, catálogo y administración de la oferta.
- `pedidos/`: creación de pedidos, detalles del pedido y control de stock.

---

## Rutas principales

| Funcionalidad | Ruta |
|---|---|
| Catálogo | `/` |
| Registro | `/auth/registro/` |
| Inicio de sesión | `/auth/login/` |
| Panel de comprador | `/auth/panel-comprador/` |
| Panel de vendedor | `/auth/panel-vendedor/` |
| Completar perfil de vendedor | `/auth/completar-perfil-vendedor/` |
| Mis productos | `/mis-productos/` |
| Nuevo producto | `/mis-productos/nuevo/` |
| Mis pedidos del comprador | `/pedidos/mis-pedidos/` |
| Detalle de un pedido propio | `/pedidos/<id>/` |

La creación de pedidos forma parte del flujo de reserva disponible directamente desde el catálogo.

---

## Modelo de datos

El sistema se organiza principalmente en torno a las siguientes entidades:

- `Usuario`: representa una cuenta y su rol dentro de la plataforma.
- `Vendedor`: representa el perfil asociado a una cuenta vendedora.
- `Producto`: representa un producto publicado, junto con su precio, stock y disponibilidad.
- `Categoria`: permite clasificar los productos publicados.
- `Pedido`: representa un pedido realizado por una persona compradora e incluye su fecha de creación y estado.
- `DetallePedido`: relaciona un pedido con los productos solicitados y sus cantidades.

---

## Datos iniciales

El proyecto incluye categorías iniciales mediante una fixture ubicada en:

```text
productos/fixtures/categorias.json
```

Estas pueden cargarse mediante:

```bash
python manage.py loaddata categorias
```

## Verificación

Con el entorno virtual activado y desde `u-pedidos/`:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Las pruebas usan una base de datos temporal. Incluyen creación de pedidos, control de stock, consulta de pedidos propios, restricciones de acceso, filtros de estado y confirmación con importes decimales.
