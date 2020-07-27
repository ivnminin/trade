import enum, random
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


class TypeDealer(enum.Enum):

    local = 1
    nl_dealer = 2

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class NameTask(enum.Enum):

    sending_email = "SENDING EMAIL"
    updating_structure_of_catalog = "UPDATING STRUCTURE OF CATALOG"
    updating_positions = "UPDATING POSITIONS"


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    success = db.Column(db.Boolean(), default=False)

    changes = db.Column(db.Boolean(), default=False)
    added = db.Column(db.Boolean(), default=False)
    removed = db.Column(db.Boolean(), default=False)

    result_msg = db.Column(db.String(51200))

    timestamp_created = db.Column(db.DateTime, default=datetime.now)
    timestamp_updated = db.Column(db.DateTime, onupdate=datetime.now)


def slug_unique_check_category(text, uids):
    if text in uids:
        return False
    return not Category.query.filter_by(slug=text).first()


slugify_unique_category = UniqueSlugify(unique_check=slug_unique_check_category, to_lower=True,
                                        max_length = 512, pretranslate=CYRILLIC)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
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
    positions = db.relationship("Position", backref="owner")
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

    def get_subcategories_have_leaves(self):
        categories_have_leaves = []
        for child in self.children:
            for category_has_leaves in child.children:
               if category_has_leaves and category_has_leaves.nl_leaf:
                   categories_have_leaves.append(category_has_leaves)

        return categories_have_leaves

    # def get_positions(self):
    #     positions = []
    #     categories_have_leaves = self.get_subcategories_have_leaves()
    #     for category_has_leaves in categories_have_leaves:
    #         if category_has_leaves and category_has_leaves.nl_leaf:
    #             positions.extend(category_has_leaves.positions)
    #
    #     return positions

    def get_subcategories(self):
        categories = []
        for category in self.children:
            categories.append(category)

            for category_second in category.children:
                categories.append(category_second)
                if category_second.children:
                    for category_third in category_second.children:
                        categories.append(category_third)

        return categories


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


def slug_unique_check_position(text, uids):
    if text in uids:
        return False
    return not Position.query.filter_by(slug=text).first()


slugify_unique_position = UniqueSlugify(unique_check=slug_unique_check_position, to_lower=True,
                                        max_length = 1024, pretranslate=CYRILLIC)


class Position(db.Model):
    __tablename__ = "positions"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    name = db.Column(db.String(1024))
    slug = db.Column(db.String(1024), unique=True)
    article = db.Column(db.String(12), unique=True)

    nl_pn = db.Column(db.String(64))
    nl_id = db.Column(db.Integer, unique=True)
    nl_nds = db.Column(db.String(64))
    nl_weight = db.Column(db.String(64))
    nl_warranty = db.Column(db.String(64))
    nl_transit_date = db.Column(db.String(64), nullable=True)
    nl_transit_count = db.Column(db.Numeric(10, 2))
    nl_count_kalujskaya = db.Column(db.Numeric(10, 2))
    nl_count_kurskaya = db.Column(db.Numeric(10, 2))
    nl_count_lobnenskaya = db.Column(db.Numeric(10, 2))
    nl_volume = db.Column(db.Numeric(10, 6))
    nl_manufacturer = db.Column(db.String(1024))
    nl_discontinued = db.Column(db.Boolean())
    nl_removed = db.Column(db.Boolean())
    nl_remote_warehouse = db.Column(db.String(64))
    nl_price_by_category_a = db.Column(db.Numeric(10, 2))
    nl_price_by_category_b = db.Column(db.Numeric(10, 2))
    nl_price_by_category_c = db.Column(db.Numeric(10, 2))
    nl_price_by_category_d = db.Column(db.Numeric(10, 2))
    nl_price_by_category_e = db.Column(db.Numeric(10, 2))
    nl_price_by_category_f = db.Column(db.Numeric(10, 2))
    nl_price_by_category_n = db.Column(db.Numeric(10, 2))

    characteristics = db.relationship("Characteristic", backref="owner")
    # images = db.relationship("Image", secondary=association_table_image_for_position)
    price = db.Column(db.Numeric(10, 0))
    count = db.Column(db.Integer)

    name_alternative = db.Column(db.String(1024), nullable=True)
    turn = db.Column(db.Boolean(), default=True)
    # dealer = db.Column(db.Enum(TypeDealer), default=TypeDealer.local)
    timestamp_created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    timestamp_updated = db.Column(db.DateTime, index=True, onupdate=datetime.utcnow)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Position {}>".format(self.name)

    @property
    def get_name(self):
        return self.name if not self.name_alternative else self.name_alternative

    @property
    def get_image(self):
        return "default.jpg"

    @property
    def get_price(self):
        return "{} руб.".format(self.price)

    # @property
    # def next_date_price_change(self):
    #     settings = Setting.query.order_by(Setting.id.desc()).first()
    #     delta = settings.price_next_date_update - datetime.utcnow()
    #     delta_days = delta.days
    #     if delta_days <= 0:
    #         return "завтра"
    #     elif delta_days and str(delta_days)[-1] == "1":
    #         return "через {} день".format(delta_days)
    #     elif delta_days and str(delta_days)[-1] in ("2", "3", "4"):
    #         return "через {} дня".format(delta_days)
    #     return "через {} дней".format(delta_days)

    # def _filter_characteristics(self, characteristics):
    #     characteristics_after_filter = [characteristic for characteristic in characteristics if characteristic.turn]
    #     def find_position_characteristic(name):
    #         try:
    #             p = [characteristic.name for characteristic in characteristics_after_filter]
    #             position_characteristic = p.index(name)
    #         except ValueError:
    #             pass
    #         else:
    #             return position_characteristic
    #
    #     item = find_position_characteristic("сайт производителя")
    #     if item:
    #         characteristics_after_filter.append(characteristics_after_filter.pop(item))
    #
    #     def change_position(item):
    #         characteristics_after_filter.insert(0, characteristics_after_filter.pop(item))
    #
    #
    #     item = find_position_characteristic("описание")
    #     if item:
    #         change_position(item)
    #
    #     item = find_position_characteristic("Назначение")
    #     if item:
    #         change_position(item)
    #
    #     item = find_position_characteristic("название")
    #     if item:
    #         change_position(item)
    #
    #     return characteristics_after_filter
    #
    # def get_characteristics(self):
    #
    #     return self._filter_characteristics(self.characteristics)
    #
    @staticmethod
    def get_len_el_to_db(category_has_positions):
        return len(category_has_positions["goods"])


    @classmethod
    def _generation_article(cls):
        symbols = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                   "A", "B", "C", "D", "E", "F"]
        article = "".join(random.choices(symbols, k=7))

        if db.session.query(cls).filter(cls.article == article).first():
            return cls._generation_article()
        else:
            return article


    @classmethod
    def update_position(cls, position):

        position_for_update = db.session.query(cls).filter(cls.nl_id == position.nl_id).first()
        position_for_update.nl_transit_date = position.nl_transit_date
        position_for_update.nl_transit_count = position.nl_transit_count
        position_for_update.nl_count_kalujskaya = position.nl_count_kalujskaya
        position_for_update.nl_count_kurskaya = position.nl_count_kurskaya
        position_for_update.nl_count_lobnenskaya = position.nl_count_lobnenskaya
        position_for_update.nl_volume = position.nl_volume
        position_for_update.nl_manufacturer = position.nl_manufacturer
        position_for_update.nl_discontinued = position.nl_discontinued
        position_for_update.nl_removed = position.nl_removed
        position_for_update.nl_remote_warehouse = position.nl_remote_warehouse
        position_for_update.nl_price_by_category_a = position.nl_price_by_category_a
        position_for_update.nl_price_by_category_b = position.nl_price_by_category_b
        position_for_update.nl_price_by_category_c = position.nl_price_by_category_c
        position_for_update.nl_price_by_category_d = position.nl_price_by_category_d
        position_for_update.nl_price_by_category_e = position.nl_price_by_category_e
        position_for_update.nl_price_by_category_f = position.nl_price_by_category_f
        position_for_update.nl_price_by_category_n = position.nl_price_by_category_n

        return position_for_update


    @classmethod
    def gen_el_to_db(cls, category_has_positions):
        if category_has_positions and category_has_positions.get("leaf"):
            if not category_has_positions.get("id"):
                raise Exception(str("not category_has_positions[id]"))
            positions = category_has_positions["goods"]
            owner = Category.query.filter_by(nl_id=category_has_positions["id"]).first()
            for position in positions:
                position = position["properties"]

                yield cls(owner=owner,
                          name=position["название"],
                          slug=slugify_unique_position(position["название"]),
                          article=cls._generation_article(),
                          nl_pn=position["PN"],
                          nl_id=int(position["id"]),
                          nl_nds=position["НДС"],
                          nl_weight=position["вес, кг"],
                          nl_warranty=position["гарантия"],
                          nl_transit_date=position["дата транзита"],
                          nl_transit_count=position["количество в транзите"],
                          nl_count_kalujskaya=position["количество на Калужской"],
                          nl_count_kurskaya=position["количество на Курской"],
                          nl_count_lobnenskaya=position["количество на Лобненской"],
                          nl_volume=position["объём, м^3"],
                          nl_manufacturer=position["производитель"],
                          nl_discontinued=position["снят с производства"],
                          nl_removed=position["удален"],
                          nl_remote_warehouse=position["удаленный склад"],
                          nl_price_by_category_a=position["цена по категории A"],
                          nl_price_by_category_b=position["цена по категории B"],
                          nl_price_by_category_c=position["цена по категории C"],
                          nl_price_by_category_d=position["цена по категории D"],
                          nl_price_by_category_e=position["цена по категории E"],
                          nl_price_by_category_f=position["цена по категории F"],
                          nl_price_by_category_n=position["цена по категории N"],
                          # dealer=TypeDealer.nl_dealer,
                          )


class Characteristic(db.Model):
    __tablename__ = "characteristics"

    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey("positions.id"))
    name = db.Column(db.String(1024))
    value = db.Column(db.String(5120))
    turn = db.Column(db.Boolean(), default=True)
    # dealer = db.Column(db.Enum(TypeDealer), default=TypeDealer.local)
    timestamp_created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    timestamp_updated = db.Column(db.DateTime, index=True, onupdate=datetime.utcnow)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Characteristic {}>".format(self.name)

    @classmethod
    def gen_el_to_db(cls, position, position_has_characteristics):
        if position_has_characteristics.get("properties"):
            for name, value in position_has_characteristics["properties"].items():
                yield cls(owner=position, name=name, value=value)