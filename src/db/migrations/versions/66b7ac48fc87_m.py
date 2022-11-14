"""-m

Revision ID: 66b7ac48fc87
Revises: 
Create Date: 2022-11-09 12:32:56.769616

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '66b7ac48fc87'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lists',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('active', 'inactive', name='ck_modellist_status', native_enum=False, create_constraint=True, length=255), server_default='active', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_lists'))
    )
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=False),
    sa.Column('last_name', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=255), nullable=False),
    sa.Column('city', sa.String(length=255), nullable=False),
    sa.Column('status', sa.Enum('active', 'inactive', name='ck_user_status', native_enum=False, create_constraint=True, length=255), server_default='active', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    op.create_table('accounts',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('account_number', sa.String(length=16), nullable=False),
    sa.Column('date', sa.Text(), nullable=True),
    sa.Column('cvv', sa.String(length=3), nullable=False),
    sa.Column('status', sa.Enum('active', 'inactive', name='ck_account_status', native_enum=False, create_constraint=True, length=255), server_default='active', nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_accounts_user_id'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_accounts'))
    )
    op.create_index(op.f('ix_accounts_user_id'), 'accounts', ['user_id'], unique=False)
    op.create_table('listitems',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('active', 'inactive', name='ck_modellist_status', native_enum=False, create_constraint=True, length=255), server_default='active', nullable=False),
    sa.Column('list_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['list_id'], ['lists.id'], name=op.f('fk_listitems_list_id'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_listitems'))
    )
    op.create_index(op.f('ix_listitems_list_id'), 'listitems', ['list_id'], unique=False)
    op.create_table('transaction',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('status', sa.Enum('active', 'inactive', name='ck_account_status', native_enum=False, create_constraint=True, length=255), server_default='active', nullable=False),
    sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_transaction_account_id'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['category_id'], ['listitems.id'], name=op.f('fk_transaction_category_id'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_transaction'))
    )
    op.create_index(op.f('ix_transaction_account_id'), 'transaction', ['account_id'], unique=False)
    op.create_index(op.f('ix_transaction_category_id'), 'transaction', ['category_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transaction_category_id'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_account_id'), table_name='transaction')
    op.drop_table('transaction')
    op.drop_index(op.f('ix_listitems_list_id'), table_name='listitems')
    op.drop_table('listitems')
    op.drop_index(op.f('ix_accounts_user_id'), table_name='accounts')
    op.drop_table('accounts')
    op.drop_table('users')
    op.drop_table('lists')
    # ### end Alembic commands ###
