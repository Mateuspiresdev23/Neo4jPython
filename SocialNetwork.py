from neo4j import GraphDatabase

class SocialNetwork:

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_person(self, name, age, location):
        with self._driver.session() as session:
            session.write_transaction(self._create_person, name, age, location)

    def _create_person(self, tx, name, age, location):
        query = (
            "CREATE (p:Person {name: $name, age: $age, location: $location})"
        )
        tx.run(query, name=name, age=age, location=location)

    def list_people(self):
        with self._driver.session() as session:
            return session.read_transaction(self._list_people)

    def _list_people(self, tx):
        query = "MATCH (p:Person) RETURN ID(p) as id, p.name as name"
        result = tx.run(query)
        return [{"id": record["id"], "name": record["name"]} for record in result]

    def add_friendship(self, person_id1, person_id2):
        with self._driver.session() as session:
            session.write_transaction(self._add_friendship, person_id1, person_id2)

    def _add_friendship(self, tx, person_id1, person_id2):
        query = (
            "MATCH (p1:Person), (p2:Person) WHERE ID(p1) = $person_id1 AND ID(p2) = $person_id2 "
            "CREATE (p1)-[:FRIEND_OF]->(p2)"
        )
        tx.run(query, person_id1=person_id1, person_id2=person_id2)

    def view_friends_network(self, person_id):
        with self._driver.session() as session:
            return session.read_transaction(self._view_friends_network, person_id)

    def _view_friends_network(self, tx, person_id):
        query = (
            "MATCH (p:Person)-[:FRIEND_OF]-(friend) WHERE ID(p) = $person_id "
            "RETURN ID(friend) as id, friend.name as name"
        )
        result = tx.run(query, person_id=person_id)
        return [{"id": record["id"], "name": record["name"]} for record in result]

    def remove_person(self, person_id):
        with self._driver.session() as session:
            session.write_transaction(self._remove_person, person_id)

    def _remove_person(self, tx, person_id):
        query = "MATCH (p:Person) WHERE ID(p) = $person_id DETACH DELETE p"
        tx.run(query, person_id=person_id)


def print_menu():
    print("\nMenu:")
    print("\n1 - Adicionar uma pessoa")
    print("\n2 - Listar as pessoas")
    print("\n3 - Adicionar amigo")
    print("\n4 - Visualizar amigos de uma pessoa")
    print("\n5 - Remover Pessoa")
    print("\n0 - Sair")

# Exemplo de uso
uri = "bolt://localhost:7687"
user = "neo4j"
password = "23100190"

social_network = SocialNetwork(uri, user, password)

while True:
    print_menu()
    choice = input("Escolha uma opção: ")

    if choice == "1":
        name = input("Nome: ")
        age = int(input("Idade: "))
        location = input("Localização: ")
        social_network.create_person(name, age, location)

    elif choice == "2":
        people = social_network.list_people()
        print("Pessoas Cadastradas:")
        for person in people:
            print(f"ID: {person['id']}, Nome: {person['name']}")

    elif choice == "3":
        person_id1 = int(input("ID da primeira pessoa: "))
        person_id2 = int(input("ID da segunda pessoa: "))
        social_network.add_friendship(person_id1, person_id2)

    elif choice == "4":
        person_id = int(input("ID da pessoa: "))
        friends_network = social_network.view_friends_network(person_id)
        print(f"\nRede de Amizades da Pessoa {person_id}:")
        for friend in friends_network:
            print(f"ID: {friend['id']}, Nome: {friend['name']}")

    elif choice == "5":
        person_id = int(input("ID da pessoa a ser removida: "))
        social_network.remove_person(person_id)

    elif choice == "0":
        break

    else:
        print("Opção inválida. Tente novamente.")

social_network.close()

