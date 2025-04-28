import os
from django.core.management.base import BaseCommand
from string import Template

# Define the default template
API_VIEW_TEMPLATE = """from base.views import BaseAPIView
from ${module}.serializers.${resource_lower} import ${resource}CreateSerializer, ${resource}ListSerializer, ${resource}UpdateSerializer, ${resource}DetailSerializer, ${resource}PartialUpdateSerializer
from base.service import ServiceFactory
from ${module}.managers.${resource_lower} import ${resource}Manager

class Base${resource}APIView(BaseAPIView):
    serializer_classes = {
        'get': None,
        'create': ${resource}CreateSerializer,
        'put': ${resource}UpdateSerializer,
        'patch': ${resource}PartialUpdateSerializer,
        'delete': None
    }
    
    serializer_response_classes = {
        'get': ${resource}ListSerializer,
        'post': ${resource}ListSerializer,
        'put': ${resource}DetailSerializer,
        'patch': ${resource}DetailSerializer,
        'delete': ${resource}DetailSerializer
    }
    
    def get_service(self, *args, **kwargs):
        request = kwargs.get('request')
        return ServiceFactory(${resource}Manager, self.get_serializer_class(request=request)))
    
    def get_serializer_class(self, *args, **kwargs):
        request = kwargs.get('request')
        method_to_action = {
            'GET': 'get',
            'POST': 'post',
            'PUT': 'put',
            'PATCH': 'patch',
            'DELETE': 'delete'
        }
        action = method_to_action.get(request.method, 'get')
        return self.serializer_classes.get(action, None)
    
    def get_response_serializer_class(self, *args, **kwargs):
        request = kwargs.get('request')
        instance_id = kwargs.get('id')
        if request.method == 'GET' and id:
            return ${resource}DetailSerializer
        
        method_to_action = {
            'GET': 'get',
            'POST': 'post',
            'PUT': 'put',
            'PATCH': 'patch',
            'DELETE': 'delete'
        }
        action = method_to_action.get(request.method)
        return self.serializer_response_classes.get(action, None)

class ${resource}APIView(Base${resource}APIView):
    def get(self, request, id=None):
        action = request.resolver_match.url_name
        return self.handle_request(request, 'get', action, query_params=request.query_params, id=id)
    
    def post(self, request):
        action = request.resolver_match.url_name
        return self.handle_request(request, 'post', action, data=request.data, query_params=request.query_params)
    
    def put(self, request, id):
        action = request.resolver_match.url_name
        return self.handle_request(request, 'put', action, data=request.data, query_params=request.query_params, id=id)
    
    def patch(self, request, id):
        action = request.resolver_match.url_name
        return self.handle_request(request, 'patch', action, data=request.data, query_params=request.query_params, id=id)
    
    def delete(self, request, id):
        action = request.resolver_match.url_name
        return self.handle_request(request, 'delete', action, id=id)
"""


class Command(BaseCommand):
    help = "Creates an API view file with specified resource and module names"

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
            template = Template(API_VIEW_TEMPLATE)

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
            self.style.SUCCESS(f"Successfully created API view file: {filepath}")
        )
