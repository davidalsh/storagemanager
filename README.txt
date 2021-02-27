Database: shop_storage
    Tables: date, product_description, products, trash, users


shop_storage
    ↳ date
    ↳ product_description
    ↳ products
    ↳ users
    ↳ trash


date:

     Column      |         Type          | Collation | Nullable |             Default
-----------------+-----------------------+-----------+----------+----------------------------------
 id              | integer               |           | not null | nextval('date_id_seq'::regclass)
 name            | character varying(50) |           |          |
 product_type    | character varying(50) |           |          |
 come_date       | date                  |           |          |
 expiration_date | integer               |           |          |

Indexes:
    "date_pkey" PRIMARY KEY, btree (id)


product_description:

   Column    |          Type          | Collation | Nullable |                     Default
-------------+------------------------+-----------+----------+-------------------------------------------------
 id          | integer                |           | not null | nextval('product_description_id_seq'::regclass)
 name        | character varying(50)  |           |          |
 description | character varying(230) |           |          |


products:

 Column |         Type          | Collation | Nullable |               Default
--------+-----------------------+-----------+----------+--------------------------------------
 id     | integer               |           | not null | nextval('products_id_seq'::regclass)
 name   | character varying(50) |           |          |
 cost   | real                  |           |          |

Indexes:
    "products_pkey" PRIMARY KEY, btree (id)


users:

   Column    |         Type          | Collation | Nullable |              Default
-------------+-----------------------+-----------+----------+-----------------------------------
 id          | integer               |           | not null | nextval('users_id_seq'::regclass)
 login       | character varying(30) |           |          |
 password    | character varying(30) |           |          |
 permissions | character varying(30) |           |          |


trash:

    Column    |         Type          | Collation | Nullable |              Default
--------------+-----------------------+-----------+----------+-----------------------------------
 id           | integer               |           | not null | nextval('trash_id_seq'::regclass)
 name         | character varying(50) |           |          |
 product_type | character varying(50) |           |          |
 come_date    | date                  |           |          |




===================================================================================================
CREATE TABLE date(
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(50),
    product_type VARCHAR(50),
    come_date date,
    expiration_date INT
);

CREATE TABLE product_description(
    id SERIAL NOT NULL,
    name VARCHAR(50),
    description VARCHAR(230)
);

CREATE TABLE products(
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(50),
    cost REAL
);

CREATE TABLE users(
    id SERIAL NOT NULL,
    login VARCHAR(30),
    password VARCHAR(30),
    permissions VARCHAR(30)
);

CREATE TABLE trash(
    id SERIAL NOT NULL,
    name VARCHAR(50),
    product_type VARCHAR(50),
    come_date date
);

===================================================================================================
admin

login: root
password: root

INSERT INTO users(login, password, permissions) VALUES('root', 'cm9vdA==', 'admin');
