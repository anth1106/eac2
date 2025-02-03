from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By

class MySeleniumTests(StaticLiveServerTestCase):
 
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        # creem superusuari
        user = User.objects.create_user("isard", "isard@example.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        # tanquem browser
        # comentar la propera línia si volem veure el resultat de l'execució al navegador
        cls.selenium.quit()
        super().tearDownClass()

    def login_user(self, username, password):
        # Ir a la página de login del admin
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        
        # Iniciar sesión
        self.selenium.find_element(By.NAME, "username").send_keys(username)
        self.selenium.find_element(By.NAME, "password").send_keys(password)
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()
		
    def create_group(self, nombre):
        # Ir a la página de grupos
        self.selenium.get(f"{self.live_server_url}/admin/auth/group/add/")
        # Crear grupo 'profe'
        group_name_input = self.selenium.find_element(By.NAME, "name")
        group_name_input.send_keys(nombre)
        self.selenium.find_element(By.NAME, "_save").click()

    def create_user(self, username, password):
        # Crear usuario
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/add/")
    
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys(username)
        password1_input = self.selenium.find_element(By.NAME, "password1")
        password1_input.send_keys(password)
        password2_input = self.selenium.find_element(By.NAME, "password2")
        password2_input.send_keys(password)
        self.selenium.find_element(By.NAME, "_save").click()

    def assign_group(self, name, isStaff):
        group_select = self.selenium.find_element(By.NAME, "groups")
        group_select.send_keys(name)
		
        # Dar permisos de staff
        if isStaff:
            self.selenium.find_element(By.NAME, "is_staff").click()
			
        self.selenium.find_element(By.NAME, "_save").click()

    def test_create_groups_and_users(self):
        # Iniciar sesión como superusuario
        self.login_user("isard", "pirineus")
        # Verificar que estamos en el panel de administración
        self.assertEqual(self.selenium.title, "Site administration | Django site admin")

        #Crear grupos
        self.create_group("profe")
        self.create_group("alumne")

        # Crear usuario 'profesor'
        self.create_user("profesor", "pass123.")

        # Ir a la lista de usuarios
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/")
        # Hacer clic en el usuario 'profesor'
        self.selenium.find_element(By.XPATH, '//table//a[contains(text(), "profesor")]').click()

        # Asignarlo al grupo 'profe'
        self.assign_group("profe", True)

        # Crear usuario 'alumno' sin permisos
        self.create_user("alumno", "pass123.")
        # Ir a la lista de usuarios
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/")
        # Hacer clic en el usuario 'alumno'
        self.selenium.find_element(By.XPATH, '//table//a[contains(text(), "alumno")]').click()
        # Asignarlo al grupo 'alumne'
        self.assign_group("alumne", False)

        # **Verificación de accesos**
        # Cerrar sesión del admin
        self.selenium.find_element(By.ID, "logout-form").click()
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        self.assertEqual(self.selenium.title, "Log in | Django site admin")

        # Intentar iniciar sesión con 'profesor'
        self.login_user("profesor", "pass123.")
        self.assertEqual(self.selenium.title, "Site administration | Django site admin")

        # Cerrar sesión de 'profesor'
        self.selenium.find_element(By.ID, "logout-form").click()

        # Intentar iniciar sesión con 'alumno' (NO debe acceder)
        self.login_user("alumno", "pass123.")

        # Comprobar que 'alumno' NO puede acceder
        self.assertEqual(self.selenium.title, "Log in | Django site admin")
		
    def test_noExistObject(self):
        try:
            self.selenium.find_element(By.XPATH,"//a[text()='Log out']")
            assert False, "Trobat element que NO hi ha de ser"
        except NoSuchElementException:
            pass
