import sqlalchemy as sa


def zero_if_none(col):
    return sa.case([(col.isnot(None), col)], else_=sa.literal_column("0"))
