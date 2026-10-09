# U-Pedidos
U-Pedidos es una aplicación web desarrollada para el curso **CC4401 – Ingeniería de Software** de la Universidad de Chile. Su objetivo es facilitar la coordinación entre personas que venden comida dentro de la comunidad universitaria y estudiantes que desean comprarla, centralizando la publicación de productos y la realización de pedidos anticipados.

**Equipo 2**.
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

## Tecnologías utilizadas
- Python
- Django **6.1.1**
- SQLite
- HTML
- CSS


## Estructura principal del proyecto

```text
2026-2-CC4401-grupo-2-main/
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
