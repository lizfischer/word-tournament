"""users table

Revision ID: f8e890de3bca
Revises: 
Create Date: 2019-07-21 23:34:52.206404

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8e890de3bca'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=45), nullable=True),
    sa.Column('password', sa.String(length=45), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('word',
    sa.Column('word', sa.String(length=45), nullable=False),
    sa.Column('rounds_done', sa.Integer(), nullable=True),
    sa.Column('matched', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('word')
    )
    op.create_table('match',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('round', sa.Integer(), nullable=True),
    sa.Column('finished', sa.Boolean(), nullable=True),
    sa.Column('word_1', sa.String(length=45), nullable=True),
    sa.Column('word_2', sa.String(length=45), nullable=True),
    sa.Column('winner', sa.String(length=45), nullable=True),
    sa.ForeignKeyConstraint(['winner'], ['word.word'], ),
    sa.ForeignKeyConstraint(['word_1'], ['word.word'], ),
    sa.ForeignKeyConstraint(['word_2'], ['word.word'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vote',
    sa.Column('match', sa.Integer(), nullable=False),
    sa.Column('user', sa.Integer(), nullable=False),
    sa.Column('vote', sa.String(length=45), nullable=True),
    sa.ForeignKeyConstraint(['match'], ['match.id'], ),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.ForeignKeyConstraint(['vote'], ['word.word'], ),
    sa.PrimaryKeyConstraint('match', 'user')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vote')
    op.drop_table('match')
    op.drop_table('word')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
