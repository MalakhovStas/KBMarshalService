class SessionDebtor:
    """Класс для хранения данных должника в сессии"""
    def __init__(self, name: str, surname: str, patronymic: str, date_birth: str, ser_num_pass: str,
                 date_issue_pass: str, name_org_pass: str, fns_key: str | None = None, fssp_key: str | None = None):
        self.surname = surname
        self.name = name
        self.patronymic = patronymic
        self.date_birth = date_birth
        self.ser_num_pass = ser_num_pass
        self.date_issue_pass = date_issue_pass
        self.name_org_pass = name_org_pass
        self.INN = None
        self.isp_prs = None
        self.ready_for_req_fns_service = True if (self.surname and self.name and self.date_birth and self.ser_num_pass and self.date_issue_pass) else False
        self.ready_for_req_fssp_service = True if (self.surname and self.name and self.date_birth) else False

        self.fssp_url = f'https://api.damia.ru/fssp/ispsfl?fam={self.surname}&nam={self.name}&otch=' \
                        f'{self.patronymic if self.patronymic else None}&bdate={self.date_birth}&page=1&key={fssp_key}'

        self.fns_url = f'https://api-fns.ru/api/innfl?fam={self.surname}&nam={self.name}&otch=' \
                       f'{self.patronymic if self.patronymic else None}&bdate={self.date_birth}&' \
                       f'doctype=21&docno={self.ser_num_pass}&key={fns_key}'

