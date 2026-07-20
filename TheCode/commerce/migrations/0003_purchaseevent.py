# Generated manually for Google Play purchase verification.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("commerce", "0002_alter_userentitlement_unique_together_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PurchaseEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("store", models.CharField(default="google_play", max_length=30)),
                ("product_id", models.CharField(max_length=100)),
                ("purchase_token", models.CharField(max_length=512, unique=True)),
                ("order_id", models.CharField(blank=True, max_length=255, null=True)),
                ("payload_json", models.JSONField(default=dict)),
                ("verified_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="purchaseevent",
            index=models.Index(
                fields=["user", "product_id"],
                name="commerce_pu_user_id_c8afbc_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="purchaseevent",
            index=models.Index(
                fields=["order_id"],
                name="commerce_pu_order_i_9f25e8_idx",
            ),
        ),
    ]
