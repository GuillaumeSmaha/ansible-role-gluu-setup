Ansible Gluu: Setup role
==========

**gluu-setup** is an Ansible role to easily install a Gluu server, its modules and the certificate.

In cluster mode, the role will install the SSH key to allow acces by cluster manager, dispatch public certifcates between all servers,
update LDAP server to accept external connecion and update configuration to use all LDAP servers.

To use the functionalities of the cluster mode in this role, all gluu servers have to be in the group `gluu-servers`
 and the Gluu Cluster Manager have to be in the group `gluu-cluster-manager`.


- [Requirements](#requirements)
- [Installation](#installation)
- [Update](#update)
- [Role Variables](#role-variables)
- [Deploying](#deploying)
- [Example Playbook](#example-playbook)
- [Sample projects](#sample-projects)

History
-------

Gluu's open source authentication & API access management server enables organizations to offer single sign-on, strong authentication, and centralize.

Requirements
------------

In order to deploy, you will need:

* Ansible in your deployer machine
* You also need to install this python dependency:
  - dnspython

```
$ pip install -r requirements.txt
```


Installation
------------

**gluu-setup** is an Ansible role distributed globally using [Ansible Galaxy](https://galaxy.ansible.com/). In order to install **gluu-setup** role you can use the following command.

```
$ ansible-galaxy install GuillaumeSmaha.gluu-setup
```



Update
------

If you want to update the role, you need to pass **--force** parameter when installing. Please, check the following command:

```
$ ansible-galaxy install --force GuillaumeSmaha.gluu-setup
```


Role Variables
--------------


```yaml
vars:

  # ===================================
  # Gluu on single node
  # ===================================

  # Define a custom version of the package to install.
  # To get a list of available package versions visit: https://gluu.org/docs/ce/
  gluu_version: 3.1.7

  # Define the hostname used by Gluu.
  gluu_hostname: '{{ ansible_ssh_host }}'

  # IP address of the host.
  gluu_ip: '{{ lookup("dig", "{{ gluu_internal_hostname }}.") | regex_replace("^NXDOMAIN$", "") | default(gluu_internal_hostname, true) }}'


  # List of the modules to install
  gluu_modules:
  - oxauth
  - oxtrust
  - ldap
  - httpd
  # Available modules:
  # - download_wars #Force to download war files
  # - oxauth
  # - oxtrust
  # - ldap
  # - httpd
  # - saml
  # - asimba
  # - cas
  # - oxauth-rp
  # - passport
  # - jce

  # Dictionnary of certificates for Gluu.
  # You can add the key that you want.
  # Each key have to contain the key `publicKey` and optionaly the key `privateKey` with the path of the certificate files.
  # Also when gluu_cluster = True, you can set the parameter `shareable` to copy the public key inside all others Gluu servers
  # List of official keys for Gluu:
  #   - asimba
  #   - httpd
  #   - idp-encryption
  #   - idp-signing
  #   - openldap
  #   - shipIDP
  # Example:
  #  gluu_certificates:
  #    idp-signing:
  #      publicKey: "{{ playbook_dir }}/templates/{{ inventory_dir | basename }}/certificates/idp-signing.crt"
  #      privateKey: "{{ playbook_dir }}/templates/{{ inventory_dir | basename }}/certificates/idp-signing.key"
  gluu_certificates:


  # Type of LDAP server
  # Since Gluu 3.1.2, you can choose the type of LDAP server.
  # This script only support openLDAP for LDAP replication.
  # Available LDAP server:
  # - openldap
  # - opendj
  # Default: openldap
  gluu_ldap_server: openldap

  # Custom certificate for LDAP server & client
  # Gluu oxAuth/oxTrust client need a pkcs12 file with private and public key
  # Default:
  gluu_ldap_certificate:
    cert_ca_file:
    cert_file:
    cert_key_file:

  # File to customize the LDAP schema
  gluu_ldap_custom_schema_file: custom_schema.json.default

  # You can set the LDAP password.
  # Default: Random password
  gluu_ldap_password:

  # Base inum of Gluu
  # Inum in Gluu are splitted in 3 parts:
  # - Base
  # - Parent Type for organization or appliance
  # - Parent Value for organization or appliance
  # - Type (only for organization)
  # - Value (only for organization)
  # Example: @!0000.1111.2222.3333!0001!1111.2222!0000!1111.2222 can be spliited like this:
  # - Base: @!0000.1111.2222.3333
  # - Parent Type: !0001!
  # - Parent Value: 1111.2222
  # - Type: !0000!
  # - Value: 1111.2222
  # You can found each type in the doc of Gluu: https://gluu.org/docs/ce/api-guide/api/
  # Default: Random value
  gluu_inum_base:

  # Organization inum
  # The value have to contains gluu_inum_base value !
  # Example: gluu_inum_org: "{{ gluu_inum_base }}!0001!1111.2222"
  # Default: Random value
  gluu_inum_org:

  # Appliance inum
  # The value have to contains gluu_inum_base value !
  # Example: gluu_inum_appliance: "{{ gluu_inum_base }}!0002!1111.2222"
  # Default: Random value
  gluu_inum_appliance:

  # Properties for the auto-genertared certificates (self-signed)
  gluu_certificate_properties:
    org_name: Organization
    country_code: CA
    city: Montreal
    state: QC




  # ===================================
  # Gluu on multiple nodes (cluster)
  # ===================================

  # Define if the server is in a cluster.
  # When gluu_cluster = True and if you have a cluster manager installed in the group "gluu-cluster-manager" ; then the SSH public key of the cluster manager will be copied on each GLuu server.
  gluu_cluster: False

  # Only when gluu_cluster = True.
  # The aim of this parameter is to distingish the internal hostname and the external hostname (gluu_hostname).
  # External hostname will be called from outside and it is a load balancer like nginx. All Gluu servers will be setup with the external hostname.
  # But to connect all nodes of the cluster to the LDAP servers, it needs to have an internal hostname that will not call the external hostname.
  # By default, it is equal to the gluu_hostname
  gluu_internal_hostname: '{{ gluu_hostname }}'

  # When gluu_cluster = True, define if there is multiple LDAP servers with replication.
  gluu_cluster_ldap_replication: False

  # When gluu_cluster = True and gluu_cluster_ldap_replication = True, define if the LDAP configuration will be set by ansible or with the cluster manager Web GUI.with replication.
  # With gluu_cluster_ldap_replication = False, this parameter enable the configuration EXTRA_SLAPD_ARGS="-F /opt/symas/etc/openldap/slapd.d".
  # With gluu_cluster_ldap_replication = True, the slapd.conf file will be edited to set the replication between all servers with the LDAP module
  gluu_cluster_ldap_replication_without_cluster_manager: False

  # When gluu_cluster = True, this parameter allow to set as default configuration another host configuration.
  # To use it you have to be careful with the order of execution of the ansible for each host.
  # The content of the file /opt/gluu-server-{{ gluu_version }}/install//community-edition-setup/setup.properties.last of the host defined will be copied inside the setup.properties
  # For example, after the installatinit allows to create a mirror server with the same configuration as the main server.
  gluu_install_from: main

  # When gluu_cluster = True, you can set the hostnames of external LDAP servers of Gluu.
  # By default, List of all servers with the LDAP module installed
  # For example, a simple consumer server installed only with oxauth module will use this parameter with the hostname of the two mains servers.
  # Example:
  #   gluu_ldap_hostname: 192.168.1.101:1636,192.168.1.102:1636
  gluu_ldap_hostname:
```

Deploying
---------

In order to deploy, you need to perform some steps:

* Create a new `hosts` file. Check [ansible inventory documentation](http://docs.ansible.com/intro_inventory.html) if you need help.
* Create a new playbook for deploying your app, for example, `deploy.yml`
* Set up role variables (see [Role Variables](#role-variables))
* Include the `GuillaumeSmaha.gluu-setup` role as part of a play
* Run the deployment playbook

```ansible-playbook -i hosts deploy.yml```

If everything has been set up properly, this command will install Gluu Cluster Manager on the host.


Example Playbook
----------------

In the folder, example you can check an example project that shows how to deploy.

In order to run it, you will need to have Vagrant and the role installed. Please check https://www.vagrantup.com for more information about Vagrant and our Installation section.

```
$ cd example
$ vagrant plugin install vagrant-lxc
$ vagrant plugin install vagrant-hostmanager
$ vagrant up --provider=lxc
$ ansible-galaxy install GuillaumeSmaha.gluu-setup
$ ansible-playbook -i env/ubuntu deploy.yml
$ ansible-playbook -i env/centos deploy.yml
```

Access to Gluu by going to:

https://gluu-setup-ubuntu/

or

https://gluu-setup-centos/


Sample projects
---------------
You can find a full example of a playbook here:

https://github.com/GuillaumeSmaha/ansible-gluu-playbook