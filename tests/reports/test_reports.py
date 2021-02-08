import os
import sys
from time import gmtime
import tempfile

from wapitiCore.file.reportgeneratorsxmlparser import ReportGeneratorsXMLParser
from wapitiCore.language.language import _
from wapitiCore.net.web import Request
from wapitiCore.definitions import additionals, anomalies, vulnerabilities, flatten_references


def test_reports():
    base_dir = os.path.dirname(sys.modules["wapitiCore"].__file__)
    xml_rep_gen_parser = ReportGeneratorsXMLParser()
    xml_rep_gen_parser.parse(os.path.join(base_dir, "data", "reports", "generators.xml"))

    for rep_gen_info in xml_rep_gen_parser.get_report_generators():
        report_gen = rep_gen_info.create_instance()

        report_gen.set_report_info(
            "http://perdu.com",
            "folder",
            gmtime(),
            "WAPITI_VERSION"
        )

        for vul in vulnerabilities:
            report_gen.add_vulnerability_type(
                vul.NAME,
                vul.DESCRIPTION,
                vul.SOLUTION,
                flatten_references(vul.REFERENCES)
            )

        for anomaly in anomalies:
            report_gen.add_anomaly_type(
                anomaly.NAME,
                anomaly.DESCRIPTION,
                anomaly.SOLUTION,
                flatten_references(anomaly.REFERENCES)
            )

        for additional in additionals:
            report_gen.add_additional_type(
                additional.NAME,
                additional.DESCRIPTION,
                additional.SOLUTION,
                flatten_references(additional.REFERENCES)
            )

        if rep_gen_info.name == "html":
            temp_obj = tempfile.TemporaryDirectory()

        else:
            temp_obj = tempfile.NamedTemporaryFile(delete=False)

        output = temp_obj.name

        print("Using report type '{}'".format(rep_gen_info.name))
        request = Request("http://perdu.com/riri?foo=bar")
        report_gen.add_vulnerability(
            category=_("Cross Site Scripting"),
            level=1,
            request=request,
            parameter="foo",
            info="This is dope"
        )

        request = Request("http://perdu.com/fifi?foo=bar")
        report_gen.add_anomaly(
            category=_("Internal Server Error"),
            level=2,
            request=request,
            parameter="foo",
            info="This is the way"
        )

        request = Request("http://perdu.com/?foo=bar")
        report_gen.add_additional(
            category=_("Fingerprint web technology"),
            level=3,
            request=request,
            parameter="foo",
            info="loulou"
        )

        report_gen.generate_report(output)

        if rep_gen_info.name == "html":
            output = report_gen.final_path

        with open(output) as fd:
            report = fd.read()
            assert "riri" in report
            assert "fifi" in report
            assert "loulou" in report