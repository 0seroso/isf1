from django.db import migrations, models


def copiar_precios_existentes(apps, schema_editor):
    DetallePedido = apps.get_model("pedidos", "DetallePedido")
    base_de_datos = schema_editor.connection.alias
    detalles = DetallePedido.objects.using(base_de_datos).select_related("producto")
    # Los pedidos antiguos no guardaban el precio de compra. Se conserva el
    # precio disponible al migrar para que no cambie con futuras ediciones.
    for detalle in detalles.iterator():
        detalle.precio_unitario = detalle.producto.precio
        detalle.save(using=base_de_datos, update_fields=["precio_unitario"])


class Migration(migrations.Migration):
    dependencies = [
        ("pedidos", "0003_agregar_estado_en_preparacion"),
    ]

    operations = [
        migrations.AddField(
            model_name="detallepedido",
            name="precio_unitario",
            field=models.DecimalField(max_digits=8, decimal_places=2, null=True),
        ),
        migrations.RunPython(copiar_precios_existentes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="detallepedido",
            name="precio_unitario",
            field=models.DecimalField(max_digits=8, decimal_places=2),
        ),
    ]
