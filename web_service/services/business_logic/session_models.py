import json
from typing import Optional

from django.utils.translation import gettext_lazy as _
from .loader import services_storage


class SessionDebtorModel:
    """Класс для хранения данных должника в сессии"""
    def __init__(self, surname: str,  name: str, patronymic: str,
                 date_birth: str, ser_num_pass: str, date_issue_pass: str, name_org_pass: str,
                 service: str, task_file_verification_id: str, service_key: str, inn: Optional[str] = None):
        self.surname = surname
        self.name = name
        self.patronymic = patronymic
        self.date_birth = date_birth
        self.ser_num_pass = ser_num_pass
        self.date_issue_pass = date_issue_pass
        self.name_org_pass = name_org_pass
        self.inn = inn
        self.isp_prs = None
        self.service = service
        self.task_file_verification_id = task_file_verification_id
        self.url = ''
        self.error = None
        self.debtor_in_db = False
        self.update_in_db = False
        self.all_db_operations_completed = False

        if service == "FNS":
            self.url = f'https://api-fns.ru/api/innfl?fam={self.surname}&nam={self.name}&otch=' \
                       f'{self.patronymic if self.patronymic else None}&bdate={self.date_birth}&' \
                       f'doctype=21&docno={self.ser_num_pass}&key={service_key}'

        elif service == "FSSP":
            self.url = f'https://api.damia.ru/fssp/ispsfl?fam={self.surname}&nam={self.name}&otch=' \
                       f'{self.patronymic if self.patronymic else None}&bdate={self.date_birth}&page=1&key={service_key}'

        services_storage.add(
            service=self.service,
            task_file_verification_id=self.task_file_verification_id,
            passport=self.ser_num_pass,
            data=self,
            # data=self.to_dict(),
            # data=self.to_json(),
        )

    def to_dict(self):
        return {
            'surname': self.surname,
            'name': self.name,
            'patronymic': self.patronymic,
            'date_birth': self.date_birth,
            'ser_num_pass': self.ser_num_pass,
            'date_issue_pass': self.date_issue_pass,
            'name_org_pass': self.name_org_pass,
            'inn': self.inn,
            'isp_prs': self.isp_prs,
            # 'service': self.service,
            # 'task_file_verification_id': self.task_file_verification_id,
            'url': self.url,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=True)

    def __str__(self):
        return f'{self.surname} {self.name} {self.patronymic} | {_("passport")}: {self.ser_num_pass}'


    # self.fns_url = f'https://api-fns.ru/api/innfl?fam={self.surname}&nam={self.name}&otch=' \
    #                f'{self.patronymic if self.patronymic else None}&bdate={self.date_birth}&' \
    #                f'doctype=21&docno={self.ser_num_pass}&key={Service.objects.get(title="FNS").key}'
    #
    # self.fssp_url = f'https://api.damia.ru/fssp/ispsfl?fam={self.surname}&nam={self.name}&otch=' \
    #                 f'{self.patronymic if self.patronymic else None}&bdate={self.date_birth}&page=1&key={fssp_key}'
    # self.ready_for_req_fns_service = True if (self.surname and self.name and self.date_birth and self.ser_num_pass and self.date_issue_pass) else False
    # self.ready_for_req_fssp_service = True if (self.surname and self.name and self.date_birth) else False

    # service_object = Service.objects.get(title=service)
    # if service_object.title == 'FNS':
    #     self.url = service_object.methods.get(title='get_inn').generate_url(
    #         fam=self.surname, nam=self.name, otch=self.patronymic if self.patronymic else None,
    #         bdate=self.date_birth, doctype=21, docno=self.ser_num_pass, key=service_object.key)