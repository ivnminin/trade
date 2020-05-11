import enum
from datetime import datetime
from slugify import UniqueSlugify, CYRILLIC
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager
from flask_login import (LoginManager, UserMixin, login_required,
                          login_user, current_user, logout_user)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_on = db.Column(db.DateTime(), default=datetime.now)
    updated_on = db.Column(db.DateTime(), default=datetime.now,  onupdate=datetime.now)

    users = db.relationship("User", backref="role")

    @classmethod
    def insert_roles(cls):
        for permission in current_user.config["PERMISSION"]:
            role = cls(name=permission)
            db.session.add(role)
            db.session.commit()

    @classmethod
    def choices(cls):
        r = [(role.id, role.name) for role in db.session.query(cls).all()]
        r.append((0, ""))
        return r


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.now)
    updated_on = db.Column(db.DateTime(), default=datetime.now,  onupdate=datetime.now)

    role_id = db.Column(db.Integer(), db.ForeignKey("roles.id"), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_administrator(self):
        if self.role.name == "admin":
            return True

    @property
    def is_moderator(self):
        if self.role.name in ["moderator", "admin"]:
            return True

    @property
    def is_user(self):
        if self.role.name == "user":
            return True

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)
    

def slug_unique_check_category(text, uids):
    if text in uids:
        return False
    return not Category.query.filter_by(slug=text).first()


slugify_unique_category = UniqueSlugify(unique_check=slug_unique_check_category, to_lower=True,
                                        max_length = 512, pretranslate=CYRILLIC)


class TypeDealer(enum.Enum):

    local = 1
    nl_dealer = 2

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    name = db.Column(db.String(512))
    slug = db.Column(db.String(512), unique=True)

    # all_positions_installed = db.Column(db.Boolean(), default=False)
    # all_images_installed = db.Column(db.Boolean(), default=False)

    nl_id = db.Column(db.Integer, unique=True)
    nl_parent_id = db.Column(db.Integer)
    nl_leaf = db.Column(db.Boolean(), default=False)
    nl_goods = db.Column(db.String(1024), nullable=True)

    dealer_operation = db.Column(db.Boolean(), default=False)

    children = db.relationship("Category", backref=db.backref("parent", remote_side=[id]))
    # positions = db.relationship("Position", backref="owner")
    name_alternative = db.Column(db.String(512))
    turn = db.Column(db.Boolean(), default=False)
    dealer = db.Column(db.Enum(TypeDealer), default=TypeDealer.local)
    timestamp_created = db.Column(db.DateTime, default=datetime.now)
    timestamp_updated = db.Column(db.DateTime, onupdate=datetime.now)

    # user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Category {}>".format(self.name)


    # def has_position_which_has_price_more_than_fix_price(self):
    #     for position in self.positions:
    #         self.positions

    # def get_subcategories_have_leaves(self):
    #     categories_have_leaves = []
    #     for child in self.children:
    #         for category_has_leaves in child.children:
    #            if category_has_leaves and category_has_leaves.nl_leaf:
    #                categories_have_leaves.append(category_has_leaves)
    #
    #     return categories_have_leaves

    # def get_positions(self):
    #     positions = []
    #     categories_have_leaves = self.get_subcategories_have_leaves()
    #     for category_has_leaves in categories_have_leaves:
    #         if category_has_leaves and category_has_leaves.nl_leaf:
    #             positions.extend(category_has_leaves.positions)
    #
    #     return positions

    def turn_on_dealer_operation_to_all_subcategories(self):

        for subcategory in self.children:
            subcategory.dealer_operation = True
            db.session.add(subcategory)
            db.session.commit()
            for subcategory_second in subcategory.children:
                subcategory_second.dealer_operation = True
                db.session.add(subcategory.dealer_operation)
                db.session.commit()


    @classmethod
    def gen_el_to_db(cls, el, parent):
        return cls(name=el["name"],
                   slug=slugify_unique_category(el["name"]),
                   nl_id=int(el["id"]),
                   nl_parent_id=int(el["parentId"]),
                   nl_leaf=True if el["leaf"] == True else False,
                   nl_goods=el["goods"],
                   dealer=TypeDealer.nl_dealer,
                   parent_id=parent.id)
