<h1>Installation</h1>
<ol>
	<li>
		<p>
			Clone the repository: <code>git clone https://github.com/Zaid-N-Ansari/testing.git</code><br />
			A directory called <b>testing</b> will created.
		</p>
	</li>
	<li>
		<p>
			Navigate to the directory: <code>cd testing</code>
		</p>
	</li>
	<li>
		<p>
			Create and activate virtual environment of choice.
		</p>
	</li>
	<li>
		<p>
			Install the requirements of the Django Web App on your local machine: <code>pip -r install requirements.txt</code>
		</p>
	</li>
	<li>
		<p>
			Migrate the database to the default database that Django provides <code>python manage.py makemigrations</code><br />
			Here, you will be shown the relationships that will be created ones you run the migrate command which is <code>python manage.py migrate</code>
		</p>
	</li>
	<li>
		<p>
			After successful database model creation and migration, create a superuser to oversee the management of the database, and <b>admin</b> if you may: <code>python manage.py createsuperuser</code><br />
			Fill in the details and remember the username and password you put in, if incase you aren't able to remember the password then run <code>python manage.py changepassword your.user.name</code>
		</p>
	</li>
	<li>
		<p>
			Now the system is ready to be up and running, run <code>python manage.py runserver [PortNumber:optional]</code>
		</p>
	</li>
	<li>
		<p>
			The app is ready to be unvieled before your eyes, goto <code>localhost:[8000 | PortNumber: if specified]</code>
		</p>
	</li>
	<li><p>Hooray...</p></li>
</ol>



# 🌟 Testing Project: Installation Guide

Welcome to the **Testing** project! Follow this step-by-step guide to set up and run the project locally on your machine. 🚀

## 📦 Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6+ installed on your machine.
- Git installed for cloning the repository.
- `pip` for installing dependencies.

---

## ⚙️ Installation Steps

<ol>
	<li>
		<p>
			<strong>Clone the repository:</strong> <br />
			Run the following command in your terminal to clone the repository:
		</p>
		
   ```bash
   git clone https://github.com/Zaid-N-Ansari/testing.git
This will create a directory called <strong>testing</strong>.
</li>
<li>
<p>
<strong>Navigate to the directory:</strong> <br />
Change your working directory to the project folder:
</p>

bash
Copy code
cd testing
less
Copy code
</li>
<li>
	<p>
		<strong>Create and activate a virtual environment:</strong> <br />
		Use your preferred tool (e.g., `venv` or `virtualenv`) to create and activate a virtual environment:
	</p>
	
bash
Copy code
# Using venv
python -m venv myenv

# Activate the virtual environment
# Windows
myenv\Scripts\activate
# macOS/Linux
source myenv/bin/activate
less
Copy code
</li>
<li>
	<p>
		<strong>Install the requirements:</strong> <br />
		Install all the necessary dependencies for the Django Web App:
	</p>
bash
Copy code
pip install -r requirements.txt
php
Copy code
</li>
<li>
	<p>
		<strong>Migrate the database:</strong> <br />
		Run the following commands to migrate the database to the default Django database:
	</p>
bash
Copy code
python manage.py makemigrations
python manage.py migrate
You will be shown the relationships that will be created once you run the migrate command.
</li>
<li>
<p>
<strong>Create a superuser:</strong> <br />
Create a superuser account to manage the database and the <strong>admin</strong> interface:
</p>

bash
Copy code
python manage.py createsuperuser
Fill in the details and remember the username and password. If you forget the password, you can change it using:

bash
Copy code
python manage.py changepassword your.user.name
php
Copy code
</li>
<li>
	<p>
		<strong>Run the development server:</strong> <br />
		Start the Django development server:
	</p>
bash
Copy code
python manage.py runserver [PortNumber:optional]
php
Copy code
</li>
<li>
	<p>
		<strong>Access the app:</strong> <br />
		Open your browser and go to:
	</p>
bash
Copy code
http://localhost:8000
or, if you specified a port number:

bash
Copy code
http://localhost:[PortNumber]
css
Copy code
</li>
<li>
	<p>
		<strong>Hooray! 🎉</strong> <br />
		The app is ready to be unveiled before your eyes. Enjoy exploring! 👀
	</p>
</li>
</ol>
📚 Additional Information
For more detailed information on Django setup, refer to the official Django documentation.
If you encounter any issues during the setup, feel free to open an issue in the GitHub repository or contact the maintainers.
👥 Contributors
We welcome contributions! Please check out our Contributing Guide for more details.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.