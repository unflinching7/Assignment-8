import abc
from allocation.domain import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, service_offering: model.ServiceOffering):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, service_type) -> model.ServiceOffering:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, service_offering):
        self.session.add(service_offering)

    def get(self, service_type):
        return self.session.query(model.ServiceOffering).filter_by(service_type=service_type).first()
