"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('whatsapp_number', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('timezone', sa.String(50), server_default='Asia/Jerusalem'),
        sa.Column('created_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('effective_date', sa.Date, nullable=False),
        sa.Column('calories_target', sa.Integer, server_default='2000'),
        sa.Column('protein_g', sa.Float, server_default='150'),
        sa.Column('carbs_g', sa.Float, server_default='200'),
        sa.Column('fat_g', sa.Float, server_default='70'),
        sa.Column('water_ml', sa.Integer, server_default='3000'),
        sa.Column('sleep_hours', sa.Float, server_default='8'),
        sa.Column('supplements', postgresql.JSONB, server_default='[]'),
        sa.Column('weekly_training_split', postgresql.JSONB, server_default='{}'),
        sa.Column('weekly_run_km', sa.Float, server_default='0'),
        sa.Column('weekly_run_sessions', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'nutrition_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('logged_at', sa.DateTime(timezone=True)),
        sa.Column('meal_type', sa.String(20)),
        sa.Column('source', sa.String(20)),
        sa.Column('raw_input_description', sa.Text, server_default=''),
        sa.Column('food_items', postgresql.JSONB, server_default='[]'),
        sa.Column('calories', sa.Integer, server_default='0'),
        sa.Column('protein_g', sa.Float, server_default='0'),
        sa.Column('carbs_g', sa.Float, server_default='0'),
        sa.Column('fat_g', sa.Float, server_default='0'),
        sa.Column('fiber_g', sa.Float, server_default='0'),
        sa.Column('photo_url', sa.Text, nullable=True),
        sa.Column('confidence', sa.String(10), server_default='medium'),
        sa.Column('notes', sa.Text, nullable=True),
    )

    op.create_table(
        'workout_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('logged_at', sa.DateTime(timezone=True)),
        sa.Column('workout_date', sa.Date, nullable=False),
        sa.Column('source', sa.String(20)),
        sa.Column('workout_type', sa.String(20)),
        sa.Column('exercises', postgresql.JSONB, server_default='[]'),
        sa.Column('distance_km', sa.Float, nullable=True),
        sa.Column('duration_minutes', sa.Integer, nullable=True),
        sa.Column('pace_min_per_km', sa.Float, nullable=True),
        sa.Column('strava_activity_id', sa.String(50), nullable=True),
        sa.Column('transcript', sa.Text, nullable=True),
        sa.Column('summary', sa.Text, server_default=''),
    )

    op.create_table(
        'weight_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('logged_at', sa.DateTime(timezone=True)),
        sa.Column('weight_kg', sa.Float, nullable=False),
        sa.Column('source', sa.String(20), server_default='manual'),
        sa.Column('body_fat_pct', sa.Float, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
    )

    op.create_table(
        'sleep_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('sleep_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sleep_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_hours', sa.Float, nullable=False),
        sa.Column('quality_score', sa.Integer, nullable=True),
        sa.Column('source', sa.String(20), server_default='manual'),
    )

    op.create_table(
        'water_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('logged_at', sa.DateTime(timezone=True)),
        sa.Column('amount_ml', sa.Integer, nullable=False),
    )

    op.create_table(
        'progress_photos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('taken_at', sa.DateTime(timezone=True)),
        sa.Column('week_number', sa.Integer, nullable=False),
        sa.Column('year', sa.Integer, nullable=False),
        sa.Column('category', sa.String(20), server_default='front'),
        sa.Column('storage_url', sa.Text, nullable=False),
        sa.Column('thumbnail_url', sa.Text, nullable=True),
        sa.Column('weight_kg', sa.Float, nullable=True),
        sa.Column('caption', sa.Text, nullable=True),
    )

    op.create_table(
        'weekly_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('week_start', sa.Date, nullable=False),
        sa.Column('user_stated_plan', sa.Text, server_default=''),
        sa.Column('planned_sessions', postgresql.JSONB, server_default='{}'),
        sa.Column('calendar_events', postgresql.JSONB, server_default='[]'),
        sa.Column('adaptations', postgresql.JSONB, server_default='[]'),
        sa.Column('completion_rate', sa.Float, nullable=True),
        sa.Column('review_notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'conversation_contexts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('messages', postgresql.JSONB, server_default='[]'),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'oauth_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('service', sa.String(30), nullable=False),
        sa.Column('access_token', sa.Text, nullable=False),
        sa.Column('refresh_token', sa.Text, nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scope', sa.Text, server_default=''),
        sa.Column('extra', sa.Text, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('oauth_tokens')
    op.drop_table('conversation_contexts')
    op.drop_table('weekly_plans')
    op.drop_table('progress_photos')
    op.drop_table('water_logs')
    op.drop_table('sleep_logs')
    op.drop_table('weight_logs')
    op.drop_table('workout_logs')
    op.drop_table('nutrition_logs')
    op.drop_table('goals')
    op.drop_table('users')
