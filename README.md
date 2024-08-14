# 🌟 Testing Project: Installation Guide

Welcome to the **Testing** project! Follow this step-by-step guide to set up and run the project locally on your machine. 🚀

## 📦 Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6+ installed on your machine.
- Git installed for cloning the repository.
- `pip` for installing dependencies.
<br />

## ⚙️ Installation Steps
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
			After successful database model creation and migration, create a superuser to oversee the management of the database, an <b>admin</b> if you may: <code>python manage.py createsuperuser</code><br />
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



## 📚 Additional Information
#### For more detailed information on Django setup, refer to the official Django documentation.
#### If you encounter any issues during the setup, feel free to open an issue in the GitHub repository or contact the maintainers.

## 👥 Contributors
#### We welcome contributions! Please check out our Contributing Guide for more details.

## 📄 License
#### This project is licensed under the MIT License - see the LICENSE file for details.