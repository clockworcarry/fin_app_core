from db.models import *
from py_common_utils_gh.db_utils.db_utils import SqlAlchemySessionManager

'''def create_companies_default_group():
    manager = SqlAlchemySessionManager()
    with manager.session_scope(db_url='postgresql://postgres:navo1234@localhost:5432/fin_app_core_db', template_name='default_session') as session:
        companies = session.query(Company).all()
        for cpny in companies:
            grps = session.query(Company, CompanyGroup, CompanyGroupRelation) \
                          .join(CompanyGroupRelation, Company.id == CompanyGroupRelation.company_id) \
                          .join(CompanyGroup, CompanyGroupRelation.group_id == CompanyGroup.id) \
                          .filter(Company.id == cpny.id) \
                          .all()
            
            default_grps = [grp for grp in grps if grp.name_code == cpny.ticker + ".default"]
            if len(default_grps) == 0:
                session.add(CompanyGroup(name_code=cpny.ticker + ".default", name=cpny.name + " default group", ))
            

if __name__ == "__main__":
    create_companies_default_group()'''