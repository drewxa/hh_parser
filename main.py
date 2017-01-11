# -*- coding: utf-8 -*-

import urllib2
import json
import csv


API_HOST = "http://api.hh.ru/vacancies/"


def get_json_object_vacancy_by_id(vacancy_id, api_host=API_HOST):
    url = "{}{}".format(api_host, vacancy_id)
    # print url
    return json.loads(urllib2.urlopen(url).read())


def get_request_url(addition_params, api_host=API_HOST):
    params = ""
    for k, vs in addition_params.iteritems():
        for v in vs:
            params += "{}={}&".format(k, v)

    url = "{}?{}".format(api_host, params.rstrip('&'))
    return url


def get_json_object_from_request(url):
    return json.loads(urllib2.urlopen(url).read())


def get_interesting_data(json_obj):

    def format_join(ls):
        return [",".join(ls).replace(';', ',')]

    def get_info_only_id(obj):
        return [obj["id"]]

    def get_common_info(obj):
        return [obj]

    def get_info_from_specializations(obj):
        prof_area_ids = []
        for s in obj:
            prof_area_ids.extend(get_info_only_id(s))
        return format_join(prof_area_ids)

    def get_info_from_salary(obj):
        if obj:
            return [obj["to"], obj["from"], obj["currency"]]
        else:
            return [None, None, None]

    def get_info_from_name(obj):
        return [obj.encode("utf-8", "ignore")]

    def get_info_from_key_skills(obj):
        skills = []
        for o in obj:
            skills.append(o["name"].encode("utf-8", "ignore").replace(';', ','))
        return format_join(skills)

    dict_data = {
        "id": get_common_info,
        "created_at": get_common_info,
        "published_at": get_common_info,
        "name": get_info_from_name,
        "archived": get_common_info,
        "premium": get_common_info,
        "key_skills": get_info_from_key_skills,
        "specializations": get_info_from_specializations,
        "schedule": get_info_only_id,
        "salary": get_info_from_salary,
        "experience": get_info_only_id,
        "area": get_info_only_id,
    }
    res = []

    for k, func in dict_data.iteritems():
        current_object = json_obj[k]
        res.extend(func(current_object))

    # print res
    return res


def get_column_names():
    return [
        "id",
        "created_at",
        "published_at",
        "name",
        "archived",
        "premium",
        "key_skills",
        "specializations",
        "schedule",
        "salary_to",
        "salary_from",
        "salary_cur",
        "experience",
        "area",
    ]


def parse_hh_ru(addition_params, file_name, api_host=API_HOST):
    url = get_request_url(addition_params=addition_params, api_host=api_host)
    print url
    obj = get_json_object_from_request(url)

    count = 0
    with open(file_name, 'ab') as csv_file:
        spam_writer = csv.writer(csv_file,
                                 delimiter=';',
                                 quotechar='|',
                                 quoting=csv.QUOTE_MINIMAL)

        # spam_writer.writerow(get_column_names())
        for o in obj['items']:
            j = get_json_object_vacancy_by_id(vacancy_id=o["id"])
            data = get_interesting_data(j)
            data.extend(addition_params["text"])
            spam_writer.writerow(data)
            count += 1
    return count


def inc_page(params):
    page = params["page"][0]
    params["page"][0] = page + 1
    return params


def main():
    max_page = 4
    max_per_page = 500

    key_words = [
        "java", "c++", "c#", "node.js",
        "python", "sql", "crypto", "unity",
        "3d", "tcp", "linux", "unix",
        "windows", "gpu", "hardware", "cto",
        "go", "rust", "ruby", "php",
        "opengl", "boost", "react", "swift",
        "objective", "r", "scala", "erlang",
        "vhdl", "machine learning", "lisp", "haskell",
        "perl", "delphi", "asm", "javascript",
        "mpi", "devops", "scrum", "agile",
        "openmp", "parallel", "arduino", "fpga",
        "crypto", "unity", "data mining", "bigdata"
    ]

    for word in key_words:
        print word

        addition_params = {
            "text": [word],
            "specialization": ["1"],
            "per_page": [max_per_page],
            "page": [0],
            "date_from": ["2017-01-01"],
            "date_to": ["2022-01-01"],
            "only_with_salary": ["false"],
            "vacancy_search_fields": ["name", "description", "company_name"],
            # "salary": ["100000"],
            # "currency": ["RUR"],
        }

        num_processed_items = 0

        for i in range(0, max_page, 1):
            num_added_item = parse_hh_ru(addition_params=addition_params, file_name='test.csv')
            num_processed_items += num_added_item
            if num_added_item < max_per_page:
                break
            addition_params = inc_page(params=addition_params)

        print "{} vacancies found".format(num_processed_items)


if __name__ == "__main__":
    main()
