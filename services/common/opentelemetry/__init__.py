"""OpenTelemetry distributed tracing for telco platform services."""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporters.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource

# Setup tracer provider
resource = Resource.create({"service.name": "telco-platform"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# Configure Jaeger exporter (if JAEGER_URL is set)
jaeger_endpoint = "http://jaeger:14268/api/traces"
exporter = JaegerExporter(
    endpoint=jaeger_endpoint,
)
provider.add_span_processor(BatchSpanProcessor(exporter))

# Create tracer
tracer = trace.get_tracer(__name__)
