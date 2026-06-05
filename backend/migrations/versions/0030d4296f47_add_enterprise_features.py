"""add enterprise features

Revision ID: 0030d4296f47
Revises: fb0fdcf67135
Create Date: 2026-06-04 13:47:12.499494

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0030d4296f47'
down_revision = 'fb0fdcf67135'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ward',
    sa.Column('ward_id', sa.Integer(), nullable=False),
    sa.Column('ward_name', sa.String(length=80), nullable=False),
    sa.Column('ward_type', sa.String(length=50), nullable=False),
    sa.Column('capacity', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('ward_id')
    )
    op.create_table('bed',
    sa.Column('bed_id', sa.Integer(), nullable=False),
    sa.Column('ward_id', sa.Integer(), nullable=False),
    sa.Column('bed_number', sa.String(length=20), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['ward_id'], ['ward.ward_id'], ),
    sa.PrimaryKeyConstraint('bed_id')
    )
    op.create_table('nurse',
    sa.Column('nurse_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('contact_num', sa.String(length=15), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('nurse_id')
    )
    op.create_table('inpatient_admission',
    sa.Column('admission_id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('bed_id', sa.Integer(), nullable=False),
    sa.Column('admitted_at', sa.DateTime(), nullable=False),
    sa.Column('discharged_at', sa.DateTime(), nullable=True),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['bed_id'], ['bed.bed_id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.patient_id'], ),
    sa.PrimaryKeyConstraint('admission_id')
    )
    op.create_table('insurance_policy',
    sa.Column('policy_id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('provider_name', sa.String(length=100), nullable=False),
    sa.Column('policy_number', sa.String(length=50), nullable=False),
    sa.Column('coverage_limit', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.patient_id'], ),
    sa.PrimaryKeyConstraint('policy_id')
    )
    op.create_table('lab_order',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('test_name', sa.String(length=100), nullable=False),
    sa.Column('test_type', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('result_notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor.doctor_id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.patient_id'], ),
    sa.PrimaryKeyConstraint('order_id')
    )
    op.create_table('referral',
    sa.Column('referral_id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('referring_doctor_id', sa.Integer(), nullable=False),
    sa.Column('target_hospital', sa.String(length=100), nullable=False),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.patient_id'], ),
    sa.ForeignKeyConstraint(['referring_doctor_id'], ['doctor.doctor_id'], ),
    sa.PrimaryKeyConstraint('referral_id')
    )
    op.create_table('bill',
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('appointment_id', sa.Integer(), nullable=True),
    sa.Column('admission_id', sa.Integer(), nullable=True),
    sa.Column('total_amount', sa.Float(), nullable=False),
    sa.Column('insurance_covered', sa.Float(), nullable=False),
    sa.Column('paid_amount', sa.Float(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['admission_id'], ['inpatient_admission.admission_id'], ),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointment.appointment_id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.patient_id'], ),
    sa.PrimaryKeyConstraint('bill_id')
    )
    op.create_table('nursing_note',
    sa.Column('note_id', sa.Integer(), nullable=False),
    sa.Column('admission_id', sa.Integer(), nullable=False),
    sa.Column('nurse_id', sa.Integer(), nullable=False),
    sa.Column('note_text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['admission_id'], ['inpatient_admission.admission_id'], ),
    sa.ForeignKeyConstraint(['nurse_id'], ['nurse.nurse_id'], ),
    sa.PrimaryKeyConstraint('note_id')
    )


def downgrade():
    op.drop_table('nursing_note')
    op.drop_table('bill')
    op.drop_table('referral')
    op.drop_table('lab_order')
    op.drop_table('insurance_policy')
    op.drop_table('inpatient_admission')
    op.drop_table('nurse')
    op.drop_table('bed')
    op.drop_table('ward')
