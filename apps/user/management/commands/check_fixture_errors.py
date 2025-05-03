
import json
import os
from django.core.management.base import BaseCommand
from django.apps import apps
from django.core.serializers import base
from django.core.serializers.json import Deserializer

class Command(BaseCommand):
    help = 'Check JSON fixture data for deserialization errors.'

    def add_arguments(self, parser):
        parser.add_argument('fixture_path', type=str, help='The path to the JSON fixture file')

    def handle(self, *args, **options):
        fixture_path = options['fixture_path']

        # Check if the fixture file exists
        if not os.path.exists(fixture_path):
            self.stderr.write(self.style.ERROR(f"File '{fixture_path}' does not exist."))
            return

        # Load the JSON data
        try:
            with open(fixture_path, 'r') as f:
                fixture_data = json.load(f)
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f"Invalid JSON in fixture file: {str(e)}"))
            return

        # Iterate over each item in the fixture
        for i, entry in enumerate(fixture_data):
            try:
                model_name = entry.get('model')
                if not model_name:
                    self.stderr.write(self.style.WARNING(f"Entry {i + 1} is missing the 'model' key"))
                    continue

                # Get the Django model from the string
                try:
                    app_label, model_label = model_name.split('.')
                    model = apps.get_model(app_label, model_label)
                except LookupError:
                    self.stderr.write(self.style.ERROR(f"Model '{model_name}' not found in entry {i + 1}"))
                    continue

                # Get the fields from the entry
                fields = entry.get('fields', {})
                if not fields:
                    self.stderr.write(self.style.WARNING(f"No fields found for model '{model_name}' in entry {i + 1}"))
                    continue

                # Check if all fields exist in the model
                for field_name in fields.keys():
                    if not hasattr(model, field_name):
                        self.stderr.write(self.style.ERROR(
                            f"Field '{field_name}' does not exist in model '{model_name}' (entry {i + 1})"
                        ))

                # Attempt to deserialize to catch any DeserializationError
                Deserializer([entry])

            except base.DeserializationError as e:
                self.stderr.write(self.style.ERROR(
                    f"DeserializationError in entry {i + 1}: {str(e)}"
                ))

        self.stdout.write(self.style.SUCCESS("Finished checking fixture data."))
