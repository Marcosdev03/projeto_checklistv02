import os
import sys
import traceback

# Force local settings module used for development
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local_sqlite')

try:
    import django
    django.setup()
except Exception:
    print('ERROR: failed to setup Django')
    traceback.print_exc()
    import os
    import sys
    import traceback
    from pathlib import Path

    # Ensure project root is importable so `config` settings package can be found
    BASE_DIR = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(BASE_DIR))

    # Force local settings module used for development
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local_sqlite')

    try:
        import django
        django.setup()
    except Exception:
        print('ERROR: failed to setup Django')
        traceback.print_exc()
        sys.exit(1)

    try:
        from drf_spectacular.generators import SchemaGenerator
        gen = SchemaGenerator()
        schema = gen.get_schema(request=None, public=True)
        import json
        print(json.dumps(schema, indent=2))
    except Exception:
        print('ERROR: schema generation failed')
        traceback.print_exc()
        sys.exit(2)

    print('Schema generation succeeded')
