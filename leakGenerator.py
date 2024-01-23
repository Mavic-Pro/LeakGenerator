#!/usr/bin/env python
import requests
import sys
import platform
import os.path
import json
import csv


class EmailGenerator(object):

    def __init__(self, domain, output_file_path="emaillistoutput.csv"):
        self.domain = domain
        self.output_file_path = output_file_path

    def get_email_combinations(self, name):
        name_parts = [part.lower() for part in name.split()]

        first_name = name_parts[0]
        last_name = name_parts[-1]
        middle_name = name_parts[1] if len(name_parts) > 2 else ''

        first_initial = first_name[0] if first_name else ''
        middle_initial = middle_name[0] if middle_name else ''
        last_initial = last_name[0] if last_name else ''

        combinations = [
            f"{first_name}@{self.domain}",
            f"{last_name}@{self.domain}",
            f"{first_name}{last_name}@{self.domain}",
            f"{first_name}.{last_name}@{self.domain}",
            f"{first_initial}{last_name}@{self.domain}",
            f"{first_initial}.{last_name}@{self.domain}",
            f"{first_name}{last_initial}@{self.domain}",
            f"{first_name}.{last_initial}@{self.domain}",
            f"{first_initial}{last_initial}@{self.domain}",
            f"{first_initial}.{last_initial}@{self.domain}",
            f"{last_name}{first_name}@{self.domain}",
            f"{last_name}.{first_name}@{self.domain}",
            f"{last_name}{first_initial}@{self.domain}",
            f"{last_name}.{first_initial}@{self.domain}",
            f"{last_initial}{first_name}@{self.domain}",
            f"{last_initial}.{first_name}@{self.domain}",
            f"{last_initial}{first_initial}@{self.domain}",
            f"{last_initial}.{first_initial}@{self.domain}",
            f"{first_initial}{middle_initial}{last_name}@{self.domain}",
            f"{first_initial}{middle_initial}.{last_name}@{self.domain}",
            f"{first_name}{middle_initial}{last_name}@{self.domain}",
            f"{first_name}.{middle_initial}.{last_name}@{self.domain}",
            f"{first_name}{middle_name}{last_name}@{self.domain}",
            f"{first_name}.{middle_name}.{last_name}@{self.domain}",
            # ... other combinations based on your requirements ...
        ]

        return combinations

    def generate_emails(self, names):
        all_emails = []

        for name in names:
            email_combinations = self.get_email_combinations(name)
            all_emails.extend(email_combinations)

        return all_emails

    def format_results(self, results):
        formatted_results = []

        for result in results:
            formatted_result = {
                "sources": result.get("sources", []),
                "email_only": result.get("email_only", 0),
                "line": result.get("line", ''),
                "last_breach": result.get("last_breach", '')
            }
            formatted_results.append(formatted_result)

        return formatted_results

    def _main(self):
        # Read input names from user input
        names_str = input("Enter names separated by commas (e.g., John Doe, Jane Smith): ")
        names = [name.strip() for name in names_str.split(',')]

        # Generate email combinations
        all_emails = self.generate_emails(names)

        # Open CSV file as writable
        with open(self.output_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Email", "Results"])  # Header row

            for email in all_emails:
                # Check email against LeakCheck API
                results = leakcheck_api.lookup(email)
                formatted_results = self.format_results(results)
                csv_writer.writerow([email, formatted_results])

        print(f"CSV file '{self.output_file_path}' has been created.")


class LeakCheckAPI:

    version = "1.0.2"
    headers = {"User-Agent": "PyLCAPI/{}, Python {} on {}".format(version, sys.version.split(" ")[0], platform.version())}

    def __init__(self):
        self.cfgname = ".pylcapi"
        self.cfgpath = os.path.expanduser('~') + "/" + self.cfgname
        self.config = self.__getCfg()
        self.url = "https://leakcheck.io"
        self.key = self.config.get("key")
        self.proxy = self.config.get("proxy")

    def __getCfg(self):
        if os.path.isfile(self.cfgpath):
            with open(self.cfgpath) as cfg:
                return json.load(cfg)
        else:
            with open(self.cfgpath, 'w') as cfg:
                data = {'key': '', 'proxy': ''}
                json.dump(data, cfg)
                return data

    def set_proxy(self, proxy):
        self.proxy = proxy

    def set_key(self, key):
        assert (len(key) == 40), "A key is invalid, it must be 40 characters long"
        self.key = key

    def lookup(self, query, lookup_type="auto"):
        assert(self.key != ""), f"A key is missing, use LeakCheckAPI.set_key() or specify it in config ({self.cfgpath})"

        data = {'key': self.key, 'type': lookup_type, "check": query}
        request = requests.get(self.url + "/api",
                               data,
                               headers=self.headers,
                               proxies={'https': self.proxy}
                               )

        status_code = request.status_code
        assert (status_code == 200), f"Invalid response code ({status_code}) instead of 200"

        result = request.json()
        if result.get("success") is False:
            assert (result.get("error") == "Not found"), request.json().get("error")
            return []
        else:
            return result.get("result")

    def getLimits(self):
        assert (self.key != ""), f"A key is missing, use LeakCheckAPI.set_key() or specify it in config ({self.cfgpath})"

        data = {'key': self.key, 'type': 'limits'}
        request = requests.get(self.url + "/api",
                               data,
                               headers=self.headers,
                               proxies={'https': self.proxy}
                               )

        assert (request.json().get("success") is True), request.json().get("error")

        return request.json().get("limits")

    def getIP(self):
        return requests.post(self.url + "/ip",
                             headers=self.headers,
                             proxies={'https': self.proxy}
                             ).text

    def getVersion(self):
        return self.version


if __name__ == "__main__":
    domain = input("Enter the domain: ")

    email_generator = EmailGenerator(domain)
    leakcheck_api = LeakCheckAPI()

    email_generator._main()
