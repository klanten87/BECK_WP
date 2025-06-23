import re
import csv

class static:
    prefix = ""
    io_enhet = ""
    larmarea = ""

def main():
    static.prefix = input("Vad vill du ha för prefix? ")
    static.io_enhet = input("I/O-enhet? ")
    static.larmarea = input("Larm-Area? ")

    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=';')
        csv_writer.writerow(["name", "device", "address", "datatype", "rawmin", "rawmax",
                             "engmin", "engmax", "unit", "format", "description", "alarmoptions", "trendoptions"])

    parse_symbols('PLC.tmc')

def write_to_csv(name, device, address, datatype, rawmin, rawmax,
                 engmin, engmax, unit, format, description, alarmoptions, trendoptions):
    with open('output.csv', 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=';')
        csv_writer.writerow([name, device, address, datatype, rawmin, rawmax,
                             engmin, engmax, unit, format, description, alarmoptions, trendoptions])

def extract_name(symbol):
    match = re.search(r'<Name>(.*?)</Name>', symbol)
    return match.group(1) if match else ''

def extract_description(symbol):
    comment_match = re.search(r'<Comment><!\[CDATA\[(.*?)\]\]></Comment>', symbol, re.DOTALL)
    if comment_match:
        comment = comment_match.group(1)
        if ',' in comment:
            return comment.rsplit(',', 1)[0].strip()
        return comment.strip()
    return ''

def extract_alarmoptions(symbol):
    match = re.search(r'<AlarmOptions>(.*?)</AlarmOptions>', symbol, re.DOTALL)
    text = match.group(1) if match else ''
    if ',' in text:
        return text.rsplit(',', 1)[1].strip()
    return ''

class FB3208SensorPT1K:
    def __init__(self, symbol):
        self.symbol = symbol
        self.full_name = extract_name(symbol)
        self.description = extract_description(symbol)

    def rows(self):
        rows = []

        items = [
            ("bFault", "_FAULT", "Givarfel, " + self.full_name, "DIGITAL", "", "", "", "", "", "", self.description, extract_alarmoptions(self.symbol), ""),
            ("rPV", "_PV", "Mätvärde", "REAL", "0", "0", "0", "0", "°C", "0.0", self.description, "", ""),
            ("bM", "_M", "Manuell styrning", "DIGITAL", "", "", "", "", "", "", self.description, "", ""),
            ("rOPM", "_OPM", "Manuellt värde", "FLOAT", "0", "100", "0", "100", "°C", "0.0", self.description, "", ""),
            ("udiFilterTime", "_INU6", "Filtertid", "INTEGER", "", "", "", "", "s", "0", self.description, "", ""),
            ("rOffset", "_INU5", "Offset mätvärde", "FLOAT", "-10", "10", "-10", "10", "°C", "0.0", self.description, "", ""),
            ("bFault1", "_AL8", "Givare Handställd, " + self.full_name, "DIGITAL", "", "", "", "", "", "", self.description, "", ""),
        ]

        for suffix, name_suffix, desc, datatype, rawmin, rawmax, engmin, engmax, unit, format_, comment, alarmopt, trendopt in items:
            name = static.prefix + self.full_name.replace('.', '_').replace('_3208', '') + name_suffix
            address = f"{self.full_name}.{suffix}"
            rows.append({
                'name': name,
                'device': static.io_enhet,
                'address': address,
                'datatype': datatype,
                'rawmin': rawmin,
                'rawmax': rawmax,
                'engmin': engmin,
                'engmax': engmax,
                'unit': unit,
                'format': format_,
                'description': desc,
                'alarmoptions': alarmopt,
                'trendoptions': trendopt
            })

        return rows

class FBCSP7P:
    def __init__(self, symbol):
        self.symbol = symbol
        self.full_name = extract_name(symbol)
        self.description = extract_description(symbol)

    def rows(self):
        rows = []

        items = [
            ("rOutsideTemp1", "_X1", "Utetemperatur"),
            ("rOutsideTemp2", "_X2", "Utetemperatur"),
            ("rOutsideTemp3", "_X3", "Utetemperatur"),
            ("rOutsideTemp4", "_X4", "Utetemperatur"),
            ("rOutsideTemp5", "_X5", "Utetemperatur"),
            ("rOutsideTemp6", "_X6", "Utetemperatur"),
            ("rOutsideTemp7", "_X7", "Utetemperatur"),
            ("rTempSetpoint1", "_Y1", "Utetemperatur / Börvärde"),
            ("rTempSetpoint2", "_Y2", "Utetemperatur / Börvärde"),
            ("rTempSetpoint3", "_Y3", "Utetemperatur / Börvärde"),
            ("rTempSetpoint4", "_Y4", "Utetemperatur / Börvärde"),
            ("rTempSetpoint5", "_Y5", "Utetemperatur / Börvärde"),
            ("rTempSetpoint6", "_Y6", "Utetemperatur / Börvärde"),
            ("rTempSetpoint7", "_Y7", "Utetemperatur / Börvärde"),
            ("rOffset", "_SPO", "Parallellförskjutning kurva"),
            ("rMinSetpoint", "_MIN", "Min börvärde"),
            ("rMaxSetpoint", "_MAX", "Max börvärde"),
        ]

        for suffix, name_suffix, desc in items:
            name = static.prefix + self.full_name.replace('.', '_') + name_suffix
            address = f"{self.full_name}.{suffix}"
            rows.append({
                'name': name,
                'device': static.io_enhet,
                'address': address,
                'datatype': "FLOAT",
                'rawmin': "0",
                'rawmax': "100",
                'engmin': "0",
                'engmax': "100",
                'unit': "°C",
                'format': "0.0",
                'description': desc,
                'alarmoptions': "",
                'trendoptions': "TREND"
            })

        return rows


def parse_symbols(filename):
    with open(filename, encoding='utf-8') as f:
        content = f.read()

    symbols = re.findall(r'<Symbol>(.*?)</Symbol>', content, re.DOTALL)

    type_handlers = {
    'fb3208sensorpt1k': FB3208SensorPT1K,
    'fbcsp7p': FBCSP7P,
}

    for symbol in symbols:
        name_match = re.search(r'<Name>(.*?)</Name>', symbol)
        if not name_match:
            continue
        type_match = re.search(r'<BaseType Namespace="INUlib">(.*?)</BaseType>', symbol)
        if not type_match:
            continue
        fb_type = type_match.group(1).lower()

        for key in type_handlers:
            if key in fb_type:
                klass = type_handlers[key]
                fb_obj = klass(symbol)
                for row in fb_obj.rows():
                    write_to_csv(**row)
                break

if __name__ == '__main__':
    main()
