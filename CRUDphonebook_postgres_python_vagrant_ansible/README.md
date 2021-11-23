

Python app that performs updates on a postgresql table that can be customized in whatever you want, our example is a phonebook. 

Vagrantfile that creates two vm's provisioned with Ansible:
   - database(db)
      - Ansible files: 
         - db_playbook.yml 
         - ansible.cfg (config file for Ansible)
         - vars.yml (variables file) - for security you can use a secret vault instead
         - hosts.ini
         
   - webapp 
      - Ansible files:
         - app_playbook.yml 
         - requirements.txt - used to pip install the required libraries by Python app



How to run:

```` 
git clone this repo
cd repo/CRUDphonebook_postgres_python_vagrant_ansible
vagrant up
vagrant ssh web
python3 /vagrant/crud_phonebook.py
```` 




