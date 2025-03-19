"""Create base tables

Revision ID: 00base_tables
Revises: 
Create Date: 2025-03-18 14:50:10.175025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '00base_tables'
down_revision: Union[str, None] = None  # Making this the first migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('oauth_provider', sa.String(), nullable=True),
        sa.Column('oauth_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_full_name'), 'users', ['full_name'], unique=False)
    
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=True)
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)
    
    # Create user_roles table (many-to-many relationship)
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('role_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    
    # Create service_accounts table
    op.create_table(
        'service_accounts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('api_key_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('permissions', sa.JSON(), nullable=True, default={"create_execution": True}),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_accounts_id'), 'service_accounts', ['id'], unique=True)
    op.create_index(op.f('ix_service_accounts_name'), 'service_accounts', ['name'], unique=True)
    
    # Create executions table
    op.create_table(
        'executions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('notebook_path', sa.String(), nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('output_notebook', sa.String(), nullable=True),
        sa.Column('output_html', sa.String(), nullable=True),
        sa.Column('python_version', sa.String(), nullable=True),
        sa.Column('cpu_milli', sa.Integer(), nullable=True),
        sa.Column('memory_mib', sa.Integer(), nullable=True),
        sa.Column('requirements', sa.JSON(), nullable=True),
        sa.Column('outputs', sa.JSON(), nullable=True),
        sa.Column('notebook_hash', sa.String(), nullable=True),
        sa.Column('parameters_hash', sa.String(), nullable=True),
        sa.Column('execution_hash', sa.String(), nullable=True),
        sa.Column('callback_token', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('service_account_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['service_account_id'], ['service_accounts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_executions_id'), 'executions', ['id'], unique=True)
    op.create_index(op.f('ix_executions_notebook_path'), 'executions', ['notebook_path'], unique=False)
    op.create_index(op.f('ix_executions_status'), 'executions', ['status'], unique=False)
    op.create_index(op.f('ix_executions_notebook_hash'), 'executions', ['notebook_hash'], unique=False)
    op.create_index(op.f('ix_executions_parameters_hash'), 'executions', ['parameters_hash'], unique=False)
    op.create_index(op.f('ix_executions_execution_hash'), 'executions', ['execution_hash'], unique=False)
    op.create_index(op.f('ix_executions_callback_token'), 'executions', ['callback_token'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order to avoid foreign key constraints
    op.drop_table('executions')
    op.drop_table('user_roles')
    op.drop_table('service_accounts')
    op.drop_table('roles')
    op.drop_table('users')
