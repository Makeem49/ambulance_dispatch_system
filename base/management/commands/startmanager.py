import os
from django.core.management.base import BaseCommand
from string import Template

# Define the default template
MANAGER_TEMPLATE = """from django.db import transaction
from rest_framework import status
from base.repository import Repository
from ${module}.models.${resource_lower} import ${resource}

class ${resource}Manager(object):
    repository = Repository(${resource})
    
    @classmethod
    def post(cls, *args, **kwargs):
        data = kwargs.get('data')
        
        try:
            with transaction.atomic():
                instance, error = cls.repository.create(data=data)
                if error:
                    return None, error, status.HTTP_400_BAD_REQUEST
        except Exception as error:
            return None, str(error), status.HTTP_400_BAD_REQUEST
        return instance, error, status.HTTP_201_CREATED
    
    @classmethod
    def list(cls, *args, **kwargs):
        filter_param = kwargs.get("query_params")
        id = kwargs.get("id")
        
        instances, error = cls.repository.list(filter_param=filter_param, id=id)
        return instances, error, status.HTTP_200_OK
    
    @classmethod
    def update(cls, *args, **kwargs):
        data = kwargs.get('data')
        id = kwargs.get('id')
        try:
            with transaction.atomic():
                instance, error = cls.repository.update(data=data, id=id)
                if error:
                    return None, error, status.HTTP_404_NOT_FOUND
        except Exception as error:
            return None, str(error), status.HTTP_400_BAD_REQUEST
        return instance, error, status.HTTP_201_CREATED
    
    @classmethod
    def patch(cls, *args, **kwargs):
        data = kwargs.get('data')
        id = kwargs.get('id')
        try:
            with transaction.atomic():
                instance, error = cls.repository.patch(data=data, id=id)
                if error:
                    cls.status_code = 400
                    return None, error, status.HTTP_404_NOT_FOUND
        except Exception as error:
            return None, str(error), status.HTTP_400_BAD_REQUEST
        return instance, error, status.HTTP_200_OK
    
    @classmethod
    def delete(cls, *args, **kwargs):
        id = kwargs.get('id')
        filter_param = kwargs.get('filter_param')
        try:
            with transaction.atomic():
                instance, error = cls.repository.delete(id=id, filter_param=filter_param)
                if error:
                    return None, error, status.HTTP_404_NOT_FOUND
        except Exception as error:
            return None, str(error), status.HTTP_400_BAD_REQUEST
        return instance, None, status.HTTP_200_OK
"""


class Command(BaseCommand):
    help = "Creates a manager file with specified resource and module names"

    def add_arguments(self, parser):
        parser.add_argument(
            "resource", type=str, help="Name of the resource (e.g., Country)"
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
            template = Template(MANAGER_TEMPLATE)

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
            self.style.SUCCESS(f"Successfully created manager file: {filepath}")
        )
