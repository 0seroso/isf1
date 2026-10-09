# U-Pedidos — Proyecto CC4401 Equipo 2

Aplicación web desarrollada en Django para facilitar la publicación y reserva anticipada de almuerzos y colaciones dentro de la comunidad universitaria.

Proyecto desarrollado para el curso **CC4401 — Ingeniería de Software** de la Universidad de Chile.

---

## Integrantes

- Ian Berdichewsky
- Benjamín Bolados
- Juan Pablo Carrasco
- Martín Friant
- Rodrigo Guerrero

---

## ¿Qué es U-Pedidos?

**U-Pedidos** es una plataforma web que conecta a estudiantes que buscan comprar alimentos dentro de la universidad con personas que los ofrecen.

La aplicación permite que las personas vendedoras publiquen y mantengan actualizada su oferta de productos, mientras que las personas compradoras pueden consultar el catálogo disponible y reservar un almuerzo indicando una cantidad y un horario de retiro.

El sistema distingue dos roles principales:

- **Comprador:** consulta la oferta disponible y realiza pedidos.
- **Vendedor:** publica y administra los productos que ofrece.

---

## ¿Qué problema resuelve U-Pedidos?

Los estudiantes de la comunidad universitaria tienen dificultades para conocer con anticipación qué alimentos estarán disponibles y asegurar un almuerzo para el horario en que lo necesitan.

Actualmente, la información sobre los productos disponibles y los pedidos no se gestiona de forma centralizada, lo que también dificulta que las personas vendedoras anticipen la demanda y organicen la preparación y entrega de sus productos.

**U-Pedidos** busca centralizar este proceso, permitiendo mantener una oferta actualizada y realizar reservas anticipadas desde una misma plataforma.

---

## Funcionalidades principales

### Comprador

- Registro e inicio de sesión con rol comprador.
- Acceso al catálogo de productos.
- Visualización de productos disponibles y con stock.
- Visualización de nombre, precio, vendedor, categoría e imagen.
- Filtrado del catálogo por categoría y vendedor.
- Selección de la cantidad de productos a reservar.
- Validación para impedir cantidades inválidas o superiores al stock disponible.
- Selección de una franja horaria disponible para el retiro del pedido.
- Validación de la disponibilidad del horario seleccionado.
- Registro del pedido con su horario de retiro.
- Descuento automático del stock una vez confirmada la reserva.
- Confirmación del pedido realizado.

### Vendedor

- Registro e inicio de sesión con rol vendedor.
- Creación de un perfil de vendedor.
- Publicación de nuevos productos.
- Asociación automática de cada producto con el vendedor autenticado.
- Visualización de los productos propios mediante `Mis productos`.
- Edición de productos propios.
- Eliminación de productos propios.
- Actualización del stock.
- Activación o desactivación de la disponibilidad de un producto.

### Control de acceso

La aplicación restringe las funcionalidades de acuerdo con el rol de la cuenta.

- Las personas compradoras acceden a las funcionalidades relacionadas con catálogo y pedidos.
- Las personas vendedoras acceden a las funcionalidades relacionadas con publicación y administración de productos.
- Un vendedor no puede modificar productos pertenecientes a otro vendedor.

---

## Tecnologías utilizadas

- **Python**
- **Django 6.1.1**
- **SQLite**
- **HTML**
- **CSS**
- **Git**
- **GitHub**

Las dependencias de Python utilizadas por el proyecto se encuentran especificadas en `requirements.txt`.

---

## Requisitos previos

Para ejecutar el proyecto localmente se necesita:

- Python 3
- `pip`
- Git

No es necesario instalar un servidor de base de datos externo, ya que durante el desarrollo se utiliza **SQLite**.

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/DCC-CC4401/2026-2-CC4401-grupo-2.git
cd 2026-2-CC4401-grupo-2
```

### 2. Ingresar a la carpeta del proyecto Django

```bash
cd u-pedidos
```

### 3. Crear un entorno virtual

```bash
python -m venv .venv
```

### 4. Activar el entorno virtual

En **Windows PowerShell**:

```powershell
.\.venv\Scripts\Activate.ps1
```

En **Linux/macOS**:

```bash
source .venv/bin/activate
```

### 5. Instalar las dependencias

```bash
python -m pip install -r requirements.txt
```

### 6. Aplicar las migraciones

```bash
python manage.py migrate
```

Las migraciones ya forman parte del repositorio, por lo que no es necesario ejecutar `makemigrations` para iniciar una copia existente del proyecto.

### 7. Cargar las categorías iniciales

```bash
python manage.py loaddata categorias
```

### 8. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

La aplicación quedará disponible en:

```text
http://127.0.0.1:8000/
```

Para detener el servidor se puede utilizar:

```text
Ctrl + C
```

---

## Estructura del proyecto

```text
u-pedidos/
├── manage.py
├── requirements.txt
├── upedidos_project/   # Configuración principal de Django
├── usuarios/           # Autenticación, perfiles y roles
├── productos/          # Catálogo y gestión de productos
├── pedidos/            # Pedidos y horarios de retiro
├── templates/          # Plantillas HTML
└── static/             # Archivos estáticos
```

Las aplicaciones principales son:

- `usuarios/`: registro, autenticación, perfiles y control de roles.
- `productos/`: productos, categorías, catálogo y administración de la oferta.
- `pedidos/`: creación de pedidos, detalles del pedido, stock y horarios de retiro.

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
| Administración Django | `/admin/` |

Las rutas asociadas a la creación del pedido y selección del horario forman parte del flujo de reserva disponible desde el catálogo.

---

## Modelo de datos

El sistema se organiza principalmente en torno a las siguientes entidades:

- `Usuario`: representa una cuenta y su rol dentro de la plataforma.
- `Vendedor`: representa el perfil asociado a una cuenta vendedora.
- `Producto`: representa un producto publicado, junto con su precio, stock y disponibilidad.
- `Categoria`: permite clasificar los productos publicados.
- `Pedido`: representa una reserva realizada por una persona compradora e incluye su estado y horario de retiro.
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
