from django.db.models import ManyToManyField, ForeignKey, OneToOneField
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction

from base.decorators.repository import handle_repository_exceptions


class Repository:
    def __init__(self, model) -> None:
        self.model = model

    def __extract_many_to_many_relationship(self, data: dict):
        m2m_fields = {}

        for field_name, value in list(data.items()):
            if isinstance(self.model._meta.get_field(field_name), ManyToManyField):
                m2m_fields[field_name] = value
                data.pop(field_name)
        return m2m_fields

    def __extract_foreign_key_relationship(self, data: dict):
        foreign_fields = {}
        counter = 0
        for field_name, value in list(data.items()):
            if isinstance(self.model._meta.get_field(field_name), ForeignKey):
                foreign_fields[counter] = {field_name: value}
                counter += 1
        return foreign_fields

    def __verify_foreign_key_relationship(self, foreign_data: dict):
        """Check if the related field actually present in the related database."""
        error = None
        for key, data in foreign_data.items():
            unpack_values = [(x, y) for x, y in data.items()]
            x, y = unpack_values[0]
            related_model = self.model._meta.get_field(x).related_model
            try:
                related_instance = related_model.objects.filter(id=y.id).first()
            except:
                related_instance = related_model.objects.filter(id=y).first()

            field_name = x.split("_")[0].capitalize()
            if related_instance:
                continue
            else:
                error = f"{field_name} with id of {y} does not exist."
                break

        if error:
            return error

    def __verify_many_to_many_relationship(self, m2m_data: dict):
        error = None
        for key, values in m2m_data.items():
            for value in values:
                related_model = self.model._meta.get_field(key).related_model
                related_instance = related_model.objects.filter(id=value.id).first()
                field_name = key.split("_")[0].capitalize()
                if related_instance:
                    continue
                else:
                    error = f"{field_name} with id of {value} does not exist."
                    break
            break

        if error:
            return error

    def __set_many_to_many_relationship(self, m2m_fields: dict, instance):
        for field_name, value in m2m_fields.items():
            getattr(instance, field_name).set(value)

    def __validate_relationship(self, data: dict):
        self.m2m_data = self.__extract_many_to_many_relationship(data)
        m2m_error = self.__verify_many_to_many_relationship(self.m2m_data)

        if m2m_error:
            return None, m2m_error

        foreign_data = self.__extract_foreign_key_relationship(data)
        foreign_error = self.__verify_foreign_key_relationship(foreign_data)
        if foreign_error:
            return None, foreign_error

        return True, None

    def __is_valid_lookup(self, key: str) -> bool:
        parts = key.split("__")
        current_model = self.model

        for i in range(len(parts)):
            part = parts[i]
            try:
                if isinstance(self.model._meta.get_field(part), ForeignKey):
                    field = current_model._meta.get_field(part)
                    if (
                        field.is_relation
                    ):  # Check if this part is a ForeignKey relationship
                        current_model = field.related_model
                elif isinstance(self.model._meta.get_field(part), ManyToManyField):
                    field = current_model._meta.get_field(part)
                    if (
                        field.is_relation
                    ):  # Check if this part is a ManyToManyField relationship
                        current_model = field.related_model
                elif isinstance(self.model._meta.get_field(part), OneToOneField):
                    field = current_model._meta.get_field(part)
                    if (
                        field.is_relation
                    ):  # Check if this part is a OneToOneField relationship
                        current_model = field.related_model
                else:
                    field = self.model._meta.get_field(part)
                    if field:
                        lookup = parts[i + 1]
                        if lookup and lookup not in field.get_lookups():
                            return False
                        else:
                            return True
            except FieldDoesNotExist:
                return False
        return True

    def __validate_data_keys(self, data):
        error = None
        for key, value in data.items():
            if "__" in key:
                is_valid = self.__is_valid_lookup(key)
                if not is_valid:
                    error = f"{key} field does not exist on the lookup fields"
                    break
            elif hasattr(self.model, key):
                continue
            else:
                error = f"{key} field does not exist on {self.model.__name__} model."
                break
        return error

    @handle_repository_exceptions
    def create(self, *args, **kwargs):
        data = kwargs.get("data")
        field_error = self.__validate_data_keys(data)
        if field_error:
            return None, field_error

        _, error = self.__validate_relationship(data)
        if error:
            return None, error

        # with transaction.atomic(using='default'):
        instance = self.model.objects.create(**data)
        self.__set_many_to_many_relationship(self.m2m_data, instance)
        return instance, None

    @handle_repository_exceptions
    def update(self, *args, **kwargs):
        data = kwargs.get("data")
        instance = kwargs.get("instance")
        id = kwargs.get("id")

        if instance:
            instance.save()
            return instance, None

        instance, error = Repository(self.model).get_by_id_or_filter_condition(id=id)

        if error:
            return instance, error

        field_error = self.__validate_data_keys(data)
        if field_error:
            return None, field_error

        _, error = self.__validate_relationship(data)
        if error:
            return None, error

        with transaction.atomic(using="default", savepoint=False):
            record = (
                self.model.objects.using("default")
                .select_for_update()
                .filter(id=id)
                .update(**data)
            )
            instance, _ = Repository(self.model).get_by_id_or_filter_condition(id=id)
            if instance:
                self.__set_many_to_many_relationship(self.m2m_data, instance)
        return instance, error

    @handle_repository_exceptions
    def patch(self, *args, **kwargs):
        """Patch update part of a record

        Keyword arguments:
        data -- data to update
        Return (instance, error): return a tuple of instance and error
        """
        data = kwargs.get("data")
        id = kwargs.get("id")

        field_error = self.__validate_data_keys(data)
        if field_error:
            return None, field_error

        _, error = self.__validate_relationship(data)
        if error:
            return None, error

        instance, error = Repository(self.model).get_by_id_or_filter_condition(id=id)

        if error:
            return instance, error

        with transaction.atomic():
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            instance.save()
            if instance:
                self.__set_many_to_many_relationship(self.m2m_data, instance)
        return instance, error

    @handle_repository_exceptions
    def get_by_id_or_filter_condition(self, *args, **kwargs):
        """Get records if name is used or get a single record if id of integer is used.

        Keyword arguments:
        name_or_id -- name or id of record
        Return (instance, error): return a tuple of instance and error
        """
        instance = None
        id = kwargs.get("id")
        filter_param = kwargs.get("filter_param")
        qr, error = Repository(self.model).list(id=id, filter_param=filter_param)
        if not error:
            if isinstance(id, int):
                instance = qr.filter(id=id).first()
            else:
                instance = qr.filter(**filter_param)
        if not instance:
            return None, "No record found."
        return instance, error

    @handle_repository_exceptions
    def delete(self, *args, **kwargs):
        id = kwargs.get("id")
        filter_param = kwargs.get("filter_param")
        instance, error = Repository(self.model).get_by_id_or_filter_condition(
            id=id, filter_param=filter_param
        )
        if not error:
            with transaction.atomic():
                instance.delete()
        return instance, error

    @handle_repository_exceptions
    def list(self, *args, **kwargs):
        query_params = kwargs.get("query_params")
        id = kwargs.get("id")
        qr, error = None, None
        if id:
            qr = self.model.objects.filter(id=id)
            if not qr:
                error = "No record found."
        elif query_params and not isinstance(query_params, int):
            # field_error = self.__validate_data_keys(query_params)
            # if field_error:
            #     error = field_error
            qr = self.model.objects.filter(query_params)
        else:
            qr = self.model.objects.all()
        response = qr, error
        return response
