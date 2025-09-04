from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.tenant import TenantService

def init_default_tenant():
    """Initialize default tenant schema"""
    db = SessionLocal()
    tenant_service = TenantService()
    
    try:
        # Create default tenant if not exists
        if not tenant_service.schema_exists(db, "default_tenant"):
            print("Creating default tenant schema...")
            success = tenant_service.create_tenant(db, "default_tenant")
            if success:
                print("✅ Default tenant schema created successfully")
            else:
                print("❌ Failed to create default tenant schema")
        else:
            print("✅ Default tenant schema already exists")
            
    except Exception as e:
        print(f"❌ Error initializing default tenant: {e}")
    finally:
        db.close()


def create_sample_data(schema_name: str = "default_tenant"):
    """Create sample data for testing"""
    db = SessionLocal()
    
    try:
        # Set schema context
        db.execute(text(f"SET search_path TO {schema_name}, public"))
        
        # Create sample application
        db.execute(text("""
            INSERT INTO applications (app_code, app_name, app_description)
            VALUES ('ATLAS', 'ATLAS System', 'Authentication and Authorization System')
            ON CONFLICT (app_code) DO NOTHING
        """))
        
        # Create sample user
        from app.core.security import get_password_hash
        password_hash = get_password_hash("admin123")
        
        db.execute(text("""
            INSERT INTO users (u_username, u_email, u_password_hash, u_full_name, u_status, u_email_verified)
            VALUES ('admin', 'admin@atamsindonesia.com', :password_hash, 'System Administrator', 'active', true)
            ON CONFLICT (u_username) DO NOTHING
        """), {"password_hash": password_hash})
        
        # Create sample roles
        db.execute(text("""
            INSERT INTO roles (r_app_id, r_code, r_name, r_level, r_permissions)
            SELECT 
                app.app_id, 
                'SUPER_ADMIN', 
                'Super Administrator', 
                100,
                '{"all": true}'::jsonb
            FROM applications app 
            WHERE app.app_code = 'ATLAS'
            ON CONFLICT (r_app_id, r_code) DO NOTHING
        """))
        
        db.execute(text("""
            INSERT INTO roles (r_app_id, r_code, r_name, r_level, r_permissions)
            SELECT 
                app.app_id, 
                'ADMIN', 
                'Administrator', 
                80,
                '{"users": ["read", "create", "update"], "roles": ["read", "create"]}'::jsonb
            FROM applications app 
            WHERE app.app_code = 'ATLAS'
            ON CONFLICT (r_app_id, r_code) DO NOTHING
        """))
        
        db.execute(text("""
            INSERT INTO roles (r_app_id, r_code, r_name, r_level, r_permissions)
            SELECT 
                app.app_id, 
                'USER', 
                'Regular User', 
                10,
                '{"profile": ["read", "update"]}'::jsonb
            FROM applications app 
            WHERE app.app_code = 'ATLAS'
            ON CONFLICT (r_app_id, r_code) DO NOTHING
        """))
        
        # Assign super admin role to admin user
        db.execute(text("""
            INSERT INTO user_roles (ur_user_id, ur_role_id)
            SELECT u.u_id, r.r_id
            FROM users u, roles r, applications a
            WHERE u.u_username = 'admin' 
            AND r.r_code = 'SUPER_ADMIN'
            AND r.r_app_id = a.app_id
            AND a.app_code = 'ATLAS'
            ON CONFLICT (ur_user_id, ur_role_id) DO NOTHING
        """))
        
        db.commit()
        print(f"✅ Sample data created for schema: {schema_name}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

def seed_new_tenant_data(db: Session, schema_name: str):
    """Create sample data for a new tenant"""
    try:
        # Set schema context
        db.execute(text(f"SET search_path TO {schema_name}, public"))

        # Create sample application
        db.execute(text("""
            INSERT INTO applications (app_code, app_name, app_description)
            VALUES ('ATLAS', 'ATLAS System', 'Authentication and Authorization System')
            ON CONFLICT (app_code) DO NOTHING
        """))

        # Create sample user
        from app.core.security import get_password_hash
        password_hash = get_password_hash("admin123")

        db.execute(text("""
            INSERT INTO users (u_username, u_email, u_password_hash, u_full_name, u_status, u_email_verified)
            VALUES ('admin', 'admin@atlas.local', :password_hash, 'System Administrator', 'active', true)
            ON CONFLICT (u_username) DO NOTHING
        """), {"password_hash": password_hash})

        # Create sample roles
        db.execute(text("""
            INSERT INTO roles (r_app_id, r_code, r_name, r_level, r_permissions)
            SELECT
                app.app_id,
                'SUPER_ADMIN',
                'Super Administrator',
                100,
                '{"all": true}'::jsonb
            FROM applications app
            WHERE app.app_code = 'ATLAS'
            ON CONFLICT (r_app_id, r_code) DO NOTHING
        """))

        # Assign super admin role to admin user
        db.execute(text("""
            INSERT INTO user_roles (ur_user_id, ur_role_id)
            SELECT u.u_id, r.r_id
            FROM users u, roles r, applications a
            WHERE u.u_username = 'admin'
            AND r.r_code = 'SUPER_ADMIN'
            AND r.r_app_id = a.app_id
            AND a.app_code = 'ATLAS'
            ON CONFLICT (ur_user_id, ur_role_id) DO NOTHING
        """))

        db.commit()
        print(f"✅ Sample data created for schema: {schema_name}")

    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()


if __name__ == "__main__":
    print("🚀 Initializing ATLAS database...")
    init_default_tenant()
    create_sample_data()
    print("✅ Database initialization completed!")