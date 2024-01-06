import requests
from bs4 import BeautifulSoup


class Amocrm:
    def __init__(self, host, email, password):
        self.host = host
        self.login = email
        self.password = password

    def _create_session(self):
        self.session = requests.Session()
        if "/" not in self.host[-1]:
            self.host += "/"
        if "https://" not in self.host:
            self.host = "https://" + self.host
        response = self.session.get(self.host)
        session_id = response.cookies.get("session_id")
        self.csrf_token = response.cookies.get("csrf_token")
        self.headers = {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": f"session_id={session_id}; " f"csrf_token={self.csrf_token};",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/111.0.0.0 Safari/537.36",
        }

    def _get_deal_by_fio(self, fio) -> (int, int, bool):
        response = self.session.get(
            self.host + f"ajax/v4/inbox/list?query[message]={fio}&limit={50}",
            headers=self.headers,
        )

        try:
            if len(response.json()["_embedded"]["talks"]) != 1:
                return None, None, False
            return (
                response.json()["_embedded"]["talks"][0]["entity"]["id"],
                response.json()["_embedded"]["talks"][0]["entity"]["pipeline_id"],
                True,
            )
        except:
            return None, None, False

    def _fill_field(self, field_id: int, deal_id: int, pipeline_id: int, value: str):
        data = {
            f"CFV[{field_id}]": value,
            "lead[STATUS]": "",
            "lead[PIPELINE_ID]": pipeline_id,
            "ID": deal_id,
        }
        self.session.post(
            url=self.host + f"ajax/leads/detail/", data=data, headers=self.headers
        )

    def _create_field(self, field):
        url = f"{self.host}ajax/settings/custom_fields/"
        data = {
            "action": "apply_changes",
            "cf[add][0][element_type]": 2,
            "cf[add][0][sortable]": True,
            "cf[add][0][groupable]": True,
            "cf[add][0][predefined]": False,
            "cf[add][0][type_id]": 1,
            "cf[add][0][name]": field,
            "cf[add][0][disabled]": "",
            "cf[add][0][settings][formula]": "",
            "cf[add][0][pipeline_id]": 0,
        }
        response = self.session.post(url, data=data, headers=self.headers).json()
        return response["response"]["id"][0]

    def connect(self) -> (str, bool):
        print(self.host, self.password, self.login)
        try:
            self._create_session()
            response = self.session.post(
                f"{self.host}oauth2/authorize",
                data={
                    "csrf_token": self.csrf_token,
                    "username": self.login,
                    "password": self.password,
                },
                headers=self.headers,
            )
            if response.status_code != 200:
                return "Некорректные входные данные для AmoCRM!", False

            self.headers["access_token"] = response.cookies.get("access_token")
            self.headers["refresh_token"] = response.cookies.get("refresh_token")
            return "Выполнен вход в Amocrm!", True
        except Exception as e:
            return "Проверьте соединение с AmoCRM!", False

    def get_params_information(self, fields: dict):
        result = {}
        url = f"{self.host}/leads/detail/{self.deal_id}"  # api/v4/leads/custom_fields
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, features="html.parser")
        #  print(soup)

        for field in soup.find_all(
            "div", {"class": "linked-form__field linked-form__field-text"}
        ):
            label = field.find(
                "div", {"class": "linked-form__field__label"}
            ).text.strip()
            value = (
                field.find("div", {"class": "linked-form__field__value"})
                .find("input")["value"]
                .strip()
            )
            index = field.get("data-id")
            if label in fields.keys():
                if value == "":
                    value = None

                result[label] = {
                    "active": value,
                    "values": [],
                    "type": "field",
                    "id": index,
                }

        selects = soup.find_all(
            "div", {"class": "linked-form__field linked-form__field-select"}
        )
        for select in selects:
            k = select.find("div", {"class": "linked-form__field__label"}).text
            v = select.find(
                "span", {"class": "control--select--button-inner"}
            ).text.strip()
            index = select.get("data-id")
            if k in fields.keys():
                result[k] = {"active": v, "values": [], "type": "select", "id": index}
                if result[k]["active"] == "Выбрать":
                    result[k]["active"] = None
                for v in select.find_all(
                    "li", {"class": "control--select--list--item"}
                ):
                    index = v.get("data-value")
                    if v.text.strip() != "Выбрать":
                        result[k]["values"].append(
                            {"value": v.text.strip(), "id": index}
                        )

        need_update = False
        for field in fields.keys():
            if field not in result.keys():
                self._create_field(field)
                need_update = True
        if need_update:
            return self.get_params_information(fields)
        return result

    def execute_filling(self, fields: dict, fio):
        deal_id, pipeline_id, status = self._get_deal_by_fio(fio)
        if not status:
            return
        params = self.get_params_information(fields)
        for f in fields.keys():
            if f not in params.keys():
                f_id = self._create_field(f)
            else:
                f_id = params[f]["id"]
            self._fill_field(f_id, deal_id, pipeline_id, fields[f])
