"""OpenAPI core schemas models module"""
import attr
import logging
from collections import defaultdict
import re

from jsonschema.exceptions import ValidationError

from openapi_core.schema.schemas._format import oas30_format_checker
from openapi_core.schema.schemas.enums import SchemaType
from openapi_core.schema.schemas.exceptions import (
    CastError, InvalidSchemaValue,
)
from openapi_core.schema.schemas.types import NoValue
from openapi_core.schema.schemas.util import forcebool
from openapi_core.schema.schemas.validators import OAS30Validator
from openapi_core.unmarshalling.schemas.exceptions import (
    UnmarshalValueError,
)

log = logging.getLogger(__name__)


@attr.s
class Format(object):
    unmarshal = attr.ib()
    validate = attr.ib()


class Schema(object):
    """Represents an OpenAPI Schema."""

    TYPE_CAST_CALLABLE_GETTER = {
        SchemaType.INTEGER: int,
        SchemaType.NUMBER: float,
        SchemaType.BOOLEAN: forcebool,
    }

    def __init__(
            self, schema_type=None, properties=None, items=None,
            schema_format=None, required=None, default=NoValue, nullable=False,
            enum=None, deprecated=False, all_of=None, one_of=None,
            additional_properties=True, min_items=None, max_items=None,
            min_length=None, max_length=None, pattern=None, unique_items=False,
            minimum=None, maximum=None, multiple_of=None,
            exclusive_minimum=False, exclusive_maximum=False,
            min_properties=None, max_properties=None, extensions=None,
            _source=None):
        self.type = SchemaType(schema_type)
        self.properties = properties and dict(properties) or {}
        self.items = items
        self.format = schema_format
        self.required = required or []
        self.default = default
        self.nullable = nullable
        self.enum = enum
        self.deprecated = deprecated
        self.all_of = all_of and list(all_of) or []
        self.one_of = one_of and list(one_of) or []
        self.additional_properties = additional_properties
        self.min_items = int(min_items) if min_items is not None else None
        self.max_items = int(max_items) if max_items is not None else None
        self.min_length = int(min_length) if min_length is not None else None
        self.max_length = int(max_length) if max_length is not None else None
        self.pattern = pattern and re.compile(pattern) or None
        self.unique_items = unique_items
        self.minimum = int(minimum) if minimum is not None else None
        self.maximum = int(maximum) if maximum is not None else None
        self.multiple_of = int(multiple_of)\
            if multiple_of is not None else None
        self.exclusive_minimum = exclusive_minimum
        self.exclusive_maximum = exclusive_maximum
        self.min_properties = int(min_properties)\
            if min_properties is not None else None
        self.max_properties = int(max_properties)\
            if max_properties is not None else None

        self.extensions = extensions and dict(extensions) or {}

        self._all_required_properties_cache = None
        self._all_optional_properties_cache = None

        self._source = _source

    @property
    def __dict__(self):
        return self._source or self.to_dict()

    def to_dict(self):
        from openapi_core.schema.schemas.factories import SchemaDictFactory
        return SchemaDictFactory().create(self)

    def __getitem__(self, name):
        return self.properties[name]

    def has_default(self):
        return self.default is not NoValue

    def get_all_properties(self):
        properties = self.properties.copy()

        for subschema in self.all_of:
            subschema_props = subschema.get_all_properties()
            properties.update(subschema_props)

        return properties

    def get_all_properties_names(self):
        all_properties = self.get_all_properties()
        return set(all_properties.keys())

    def get_cast_mapping(self):
        mapping = self.TYPE_CAST_CALLABLE_GETTER.copy()
        mapping.update({
            SchemaType.ARRAY: self._cast_collection,
        })

        return defaultdict(lambda: lambda x: x, mapping)

    def cast(self, value):
        """Cast value from string to schema type"""
        if value in (None, NoValue):
            return value

        cast_mapping = self.get_cast_mapping()

        cast_callable = cast_mapping[self.type]
        try:
            return cast_callable(value)
        except ValueError:
            raise CastError(value, self.type)

    def _cast_collection(self, value):
        return list(map(self.items.cast, value))

    def get_validator(self, resolver=None):
        return OAS30Validator(
            self.__dict__,
            resolver=resolver, format_checker=oas30_format_checker,
        )

    def validate(self, value, resolver=None):
        validator = self.get_validator(resolver=resolver)
        try:
            return validator.validate(value)
        except ValidationError:
            errors_iter = validator.iter_errors(value)
            raise InvalidSchemaValue(
                value, self.type, schema_errors_iter=errors_iter)

    def unmarshal(self, value, custom_formatters=None, strict=True):
        """Unmarshal parameter from the value."""
        from openapi_core.unmarshalling.schemas.factories import (
            SchemaUnmarshallersFactory,
        )
        unmarshallers_factory = SchemaUnmarshallersFactory(
            custom_formatters)
        unmarshaller = unmarshallers_factory.create(self)
        try:
            return unmarshaller(value, strict=strict)
        except ValueError as exc:
            raise UnmarshalValueError(value, self.type, exc)
