import os
from django.core.management.base import BaseCommand
from string import Template

# Define the default template
SERIALIZER_TEMPLATE = """from rest_framework import serializers
from ${module}.models.${resource_lower} import ${resource}

class ${resource}CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ${resource}
        fields = ['name']

class ${resource}ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ${resource}
        fields = '__all__'

class ${resource}UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ${resource}
        fields = '__all__'
        
class ${resource}PartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ${resource}
        fields = '__all__'
        
    def __init__(self, instance=None, data=..., **kwargs):
        print('hello')
        super().__init__(instance, data, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].required = False

class ${resource}DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ${resource}
        fields = '__all__'
"""


class Command(BaseCommand):
    help = "Creates serializer files with specified resource and module names"

    def add_arguments(self, parser):
        parser.add_argument(
            "resource", type=str, help="Name of the resource (e.g., Season)"
        )
        parser.add_argument(
            "module", type=str, help="Name of the module (e.g., location)"
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default=".",
            help="Output directory for the file (relative to project root)",
        )
        parser.add_argument(
            "--template",
            type=str,
            help="Path to custom template file (relative to project root)",
        )

    def handle(self, *args, **options):
        resource_name = options["resource"]
        module_name = options["module"]
        output_dir = options["output_dir"]
        template_path = options["template"]

        # Convert resource to lowercase for certain imports
        resource_lower = resource_name.lower()

        # Use custom template if provided, otherwise use default
        if template_path and os.path.exists(template_path):
            with open(template_path, "r") as f:
                template_content = f.read()
            template = Template(template_content)
        else:
            template = Template(SERIALIZER_TEMPLATE)

        # Substitute variables in the template
        content = template.substitute(
            resource=resource_name, resource_lower=resource_lower, module=module_name
        )

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Create the filename
        filename = f"{resource_lower}.py"
        filepath = os.path.join(output_dir, filename)

        # Write the file
        with open(filepath, "w") as f:
            f.write(content)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created serializer file: {filepath}")
        )
