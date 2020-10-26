import unittest
from flask import current_app, request, render_template, redirect, url_for
from app import app, db
from app.models import Role, Image, User, Category, Position


class BasicCaseTest(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config.from_object("config.TestingConfig")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class AppCaseTest(BasicCaseTest):
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config["TESTING"])

    def test_app_name(self):
        self.assertTrue(current_app.name == "app")


class ModelsCaseTest(BasicCaseTest):

    def setUp(self):
        super().setUp()

        Role.insert_roles()

        user_admin = User(name="Ivan", username="ivan", role=db.session.query(Role).filter_by(name="admin").first())
        user_admin.set_password("qwerty")
        user_moderator = User(name="Alex", username="alex",
                              role=db.session.query(Role).filter_by(name="moderator").first())
        user_moderator.set_password("qwerty")
        user_user = User(name="Bob", username="bob", role=db.session.query(Role).filter_by(name="user").first())
        user_user.set_password("qwerty")

        i = Image(original_name="Test_image", name="test_name")
        db.session.add_all([i, user_admin, user_moderator, user_user])
        db.session.commit()

    def test_model_tables_exists(self):
        tables_name = {"association_table_image_for_position", "categories", "characteristics", "images", "positions",
                       "roles", "tasks", "users"}
        self.assertEqual(set(db.engine.table_names()), tables_name)

    def test_model_role(self):
        roles = ["admin", "moderator", "user"]
        r = db.session.query(Role).all()
        self.assertEqual(roles, [role.name for role in r])

    def test_model_user(self):
        u_admin = db.session.query(User).filter_by(username="ivan").first()
        self.assertTrue(u_admin.is_administrator)

        u_moderator = db.session.query(User).filter_by(username="alex").first()
        self.assertTrue(u_moderator.check_password("qwerty"))

        u_user = db.session.query(User).filter(User.name=="Bob", Role.name=="user").first()
        self.assertTrue(u_user.name == "Bob")

    def test_model_category(self):
        data = {"name": "Test_category",
                "id": "123",
                "parentId": "1",
                "leaf": "true",
                "goods": "something",
                }
        categoty = Category.gen_el_to_db(data, Category(name=app.config["PRODUCT_CATALOG_ROOT_DIRECTORY"]))
        self.assertIsInstance(categoty, Category)

    def test_model_position(self):
        self.assertTrue(False)

    def test_model_characteristic(self):
        self.assertTrue(False)

    def test_model_image(self):
        original_name = "Test_image"
        i = db.session.query(Image).filter_by(original_name=original_name).first()
        self.assertTrue(i.__str__() == "test_name")


class ViewersCaseTest(BasicCaseTest):
    def setUp(self):
        super().setUp()
        self.app.config["WTF_CSRF_ENABLED"] = False

        data = {"name": "Test_category",
                "id": "123",
                "parentId": "1",
                "leaf": "true",
                "goods": "something",
                }

        root_directory = Category(name=app.config["PRODUCT_CATALOG_ROOT_DIRECTORY"])
        db.session.add(root_directory)
        db.session.commit()
        category = Category.gen_el_to_db(data, root_directory)
        db.session.add(category)
        db.session.commit()

        self.client = self.app.test_client()

    def test_view_app_index(self):
        response = self.client.get("/")
        self.assertTrue(response.status_code == 200)

        data = {"name": "Name", "description": "Description", "contact_data": "Contact"}
        response = self.client.post("/", data=data)
        self.assertTrue(response.status_code == 302)

    def test_view_app_backend(self):
        c = db.session.query(Category).filter_by(name="Test_category").first()
        self.assertFalse(c.turn == "on")

        response = self.client.get("/backend/category/turn/{}?turn=on".format(c.id))
        self.assertTrue(response.status_code == 302)

        c = db.session.query(Category).filter_by(name="Test_category").first()
        self.assertTrue(c.turn)


class FormsCaseTest(BasicCaseTest):
    def test_form_app(self):
        self.assertTrue(False)

    def test_form_app_backend(self):
        self.assertTrue(False)


class TaskerCaseTest(BasicCaseTest):
    def test_tasker_app_backend(self):
        self.assertTrue(False)


class UtilsCaseTest(BasicCaseTest):
    def test_util(self):
        self.assertTrue(False)


class AppInitCaseTest(BasicCaseTest):
    def test_init(self):
        self.assertTrue(False)