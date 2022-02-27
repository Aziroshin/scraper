from unittest.mock import MagicMock, patch

import pytest

import utils.dynamo
from scrapers.hungary_hu import HungaryScraper
from scrapers.moldova_ro import MoldovaScraper
from scrapers.poland import PolandScraper
from scrapers.poland_en import PolandENScraper


@pytest.fixture(autouse=True)
def put_item():
    """Mock dynamo.  Stupid dynamo."""
    with patch('utils.dynamo.client.put_item', MagicMock(name='put_item')) as put_item:
        yield put_item


@pytest.fixture()
def check_common(put_item):
    def func(country):
        assert put_item.called
        cargs = put_item.call_args
        assert cargs.kwargs['TableName'] == 'TechForUkraine-CIG'
        item = cargs.kwargs['Item']
        assert item
        assert item['country']
        assert item['country']['S']
        assert item['country']['S'] == country
        assert item['general']
        assert item['source']
        assert item['source']['S']
        assert item['reception']
        assert item['reception']['L'] is not None

        for reception in item['reception']['L']:
            assert set(reception.keys()) == {'M'}
            assert set(
                reception['M']) == {
                'name',
                'lat',
                'lon',
                'address',
                'qr'
            }
            for value in reception['M'].values():
                assert set(value.keys()) == {'S'}

        general = [
            line['S']
            for line in
            item['general']['L']
        ]
        reception = [
            {
                'name': rec['M']['name']['S'],
                'lat': rec['M']['lat']['S'],
                'lon': rec['M']['lon']['S'],
                'address': rec['M']['address']['S'],
                'qr': rec['M']['qr']['S'],
            }
            for rec in
            item['reception']['L']
        ]
        return item, general, reception

    return func


def test_poland_pl(put_item, check_common):
    poland_scraper = PolandScraper()
    poland_scraper.scrape_poland_pl()
    check_common('poland-pl')

def test_poland_en(put_item, check_common):
    poland_scraper = PolandScraper()
    poland_scraper.scrape_poland_en()
    check_common('poland-en')

def test_poland_ua(put_item, check_common):
    poland_scraper = PolandScraper()
    poland_scraper.scrape_poland_ua()
    check_common('poland-ua')

def test_scrape_hungary_hu(put_item, check_common):
    # This one's too big...just doing a spot check
    hungary_scraper = HungaryScraper()
    hungary_scraper.scrape()
    item, general, reception = check_common('hungary-hu')
    assert len(general) == 100

    # First
    assert 'Határátlépéssel kapcsolatos általános információk' in general
    # Some...more stuff that looks important?
    assert 'kotegyanhrk@bekes.police.hu' in general
    assert '+36-66-572-620' in general
    assert 'biharkereszteshrk@hajdu.police.hu' in general
    assert 'nyirabranyhrk@hajdu.police.hu' in general
    assert '+36-52-596-009' in general
    # Last
    assert 'Letenye Autópálya' in general
    assert len(reception) == 58

    assert reception[0] == {'name': 'Letenye I. Közúti Határátkelőhely', 'lat': '46.420334', 'lon': '16.697088', 'address': '', 'qr': ''}
    assert reception[1] == {'name': 'Letenye II. Autópálya Határátkelőhely', 'lat': '46.41246', 'lon': '16.70346', 'address': '', 'qr': ''}
    assert reception[2] == {'name': 'Murakeresztúr Vasúti Határátkelőhely', 'lat': '46.358938', 'lon': '16.85126', 'address': '', 'qr': ''}
    assert reception[-1] == {'name': 'Garbolc - Bercu', 'lat': '47.9448241', 'lon': '22.8628', 'address': '', 'qr': ''}

#FIXME: This is broken, looks like the ordering is different than expected, I'm getting address first and name last
def test_scrape_moldova_ro(put_item, check_common):
    moldova_scraper = MoldovaScraper()
    moldova_scraper.scrape()
    item, general, reception = check_common('moldova-ro')
    # I do not know what this means, but for the moment, we don't want it to
    # change significantly.
    assert general == [
        'TRAVERSAREA FRONTIEREI DE STAT MOLDO-UCRAINENE',
        'Pentru cetăţenii Republicii Moldova şi Ucrainei:',
        'Este necesar paşaportul sau buletinul de identitate (pentru locuitorii raioanelor de frontieră) în dependenţă şi în corespundere cu regulile stabilite prin «Acordul între Guvernul Republicii Moldova şi Guvernul Ucrainei cu privire la punctele de trecere la frontiera de stat moldo-ucraineană şi simplificarea formalităţilor la trecerea frontierei de către cetăţenii care locuiesc în raioanele de frontieră» semnat în or. Chişinău, pe data de 11 martie 1997.',
        'Lista raioanelor de frontieră ale Republicii Moldova, locuitorii cărora traversează frontiera de stat moldo-ucraineană în mod simplificat.',
        'Lista raioanelor de frontieră a Ucrainei, locuitorii cărora traversează frontiera de stat moldo-ucraineană în mod simplificat.',
        'Regiunea Cernăuţi :',
        'Regiunea Odesa:',
        'Mijloacele de transport traversează frontiera de stat a Republicii Moldova pe baza documentelor valabile, care permit trecerea frontierei de stat.',
        'Documentele valabile pentru mijloacele de transport, înregistrate pe teritoriul Republicii Moldova:',
        'a) permisul de conducere perfectat pe numele conducătorului auto, valabil pentru categoria (subcategoria) din care face parte autovehiculul condus; b) certificatul de înmatriculare a vehiculului; c) poliţa de asigurare obligatorie de răspundere civilă a deţinătorilor mijloacelor de transport auto; d) actele referitoare la natura şi masa încărcăturii, în cazurile stabilite de legislaţie.'
    ]
    # TODO: Don't test hundreds of lines of crap after we've finished the kml
    # migration
    assert reception == [{'name': 'Vasilcău-Velikaia Koșnița',
                          'lat': '48.1286973',
                          'lon': '28.4190675',
                          'address': '',
                          'qr': ''},
                         {'name': 'Soroca-Țekinovca',
                          'lat': '48.1631563',
                          'lon': '28.3114161',
                          'address': '',
                          'qr': ''},
                         {'name': 'Soroca-Țekinovka ',
                          'lat': '48.1432364',
                          'lon': '28.3041343',
                          'address': '',
                          'qr': ''},
                         {'name': 'Mărculești Aeroport Internațional',
                          'lat': '47.8646064',
                          'lon': '28.2180899',
                          'address': '',
                          'qr': ''},
                         {'name': 'Cosăuți-Iampol ',
                          'lat': '48.237407',
                          'lon': '28.2980678',
                          'address': '',
                          'qr': ''},
                         {'name': 'Cosăuți-Iampol ',
                          'lat': '48.227819',
                          'lon': '28.2793194',
                          'address': '',
                          'qr': ''},
                         {'name': 'Otaci-Moghileov-Podolsk',
                          'lat': '48.4428872',
                          'lon': '27.7868838',
                          'address': '',
                          'qr': ''},
                         {'name': 'Unguri-Bronița ',
                          'lat': '48.3986264',
                          'lon': '27.8756567',
                          'address': '',
                          'qr': ''},
                         {'name': 'Vălcineț-Moghileov-Podolsk',
                          'lat': '48.4430894',
                          'lon': '27.7844218',
                          'address': '',
                          'qr': ''},
                         {'name': 'Ocnița-Sokireani ',
                          'lat': '48.4384185',
                          'lon': '27.4629002',
                          'address': '',
                          'qr': ''},
                         {'name': 'Ocnița-Sokireanî',
                          'lat': '48.4359842',
                          'lon': '27.4620966',
                          'address': '',
                          'qr': ''},
                         {'name': 'Clocușna-Sokireanî ',
                          'lat': '48.4332768',
                          'lon': '27.3767242',
                          'address': '',
                          'qr': ''},
                         {'name': 'Briceni-Rossoșanî ',
                          'lat': '48.3754359',
                          'lon': '27.0488263',
                          'address': '',
                          'qr': ''},
                         {'name': 'Grimăncăuți-Vașkivțî ',
                          'lat': '48.3950352',
                          'lon': '27.1049958',
                          'address': '',
                          'qr': ''},
                         {'name': 'Larga-Kelmențî ',
                          'lat': '48.4160991',
                          'lon': '26.8267407',
                          'address': '',
                          'qr': ''},
                         {'name': 'Medveja-Zelionaia ',
                          'lat': '48.3575029',
                          'lon': '26.7622687',
                          'address': '',
                          'qr': ''},
                         {'name': 'Larga-Kelmențî ',
                          'lat': '48.4277221',
                          'lon': '27.0652115',
                          'address': '',
                          'qr': ''},
                         {'name': 'Medveja-Zelionaia ',
                          'lat': '48.3518679',
                          'lon': '26.7934087',
                          'address': '',
                          'qr': ''},
                         {'name': 'Criva-Mamaliga ',
                          'lat': '48.2652082',
                          'lon': '26.6255316',
                          'address': '',
                          'qr': ''},
                         {'name': 'Lipcani-Rădăuți Prut (SISTAT)',
                          'lat': '48.2542634',
                          'lon': '26.8015744',
                          'address': '',
                          'qr': ''},
                         {'name': 'Costești-Stînca',
                          'lat': '47.8404434',
                          'lon': '27.2274752',
                          'address': '',
                          'qr': ''},
                         {'name': 'Bălți Aeroport Internațional',
                          'lat': '47.8460281',
                          'lon': '27.7774729',
                          'address': '',
                          'qr': ''},
                         {'name': 'Sculeni-Scuelni',
                          'lat': '47.3202968',
                          'lon': '27.6102466',
                          'address': '',
                          'qr': ''},
                         {'name': 'Ungheni-Iași',
                          'lat': '47.2096047',
                          'lon': '27.7881118',
                          'address': '',
                          'qr': ''},
                         {'name': 'Leușeni-Albița',
                          'lat': '46.794229',
                          'lon': '28.1618137',
                          'address': '',
                          'qr': ''},
                         {'name': 'Cahul-Oancea',
                          'lat': '45.9168681',
                          'lon': '28.1220363',
                          'address': '',
                          'qr': ''},
                         {'name': 'Giurgiulești-Reni',
                          'lat': '45.4716336',
                          'lon': '28.1986358',
                          'address': '',
                          'qr': ''},
                         {'name': 'Giurgiulești-Galați',
                          'lat': '45.4731043',
                          'lon': '28.1982677',
                          'address': '',
                          'qr': ''},
                         {'name': 'Giurgiulești-Port',
                          'lat': '45.470935',
                          'lon': '28.2031415',
                          'address': '',
                          'qr': ''},
                         {'name': 'Giurgiulești-Reni',
                          'lat': '45.4758141',
                          'lon': '28.2069202',
                          'address': '',
                          'qr': ''},
                         {'name': 'Cișmichioi-Dolinscoe ',
                          'lat': '45.5399583',
                          'lon': '28.3454981',
                          'address': '',
                          'qr': ''},
                         {'name': 'Etulia-Fricăței',
                          'lat': '45.528986',
                          'lon': '28.4203324',
                          'address': '',
                          'qr': ''},
                         {'name': 'Vulcănești-Vinogradovka',
                          'lat': '45.6976875',
                          'lon': '28.498158',
                          'address': '',
                          'qr': ''},
                         {'name': 'Cairaclia-Zaliznicinoe',
                          'lat': '45.7675332',
                          'lon': '28.6187404',
                          'address': '',
                          'qr': ''},
                         {'name': 'Ceadîr-Lunga - Novîe-Troianî ',
                          'lat': '45.9830203',
                          'lon': '28.8444251',
                          'address': '',
                          'qr': ''},
                         {'name': 'Ceadîr-Lunga - Maloiaroslaveț ',
                          'lat': '46.079207',
                          'lon': '28.966093',
                          'address': '',
                          'qr': ''},
                         {'name': 'Basarabeasca-Serpniovo ',
                          'lat': '46.324282',
                          'lon': '28.9883993',
                          'address': '',
                          'qr': ''},
                         {'name': 'Aeroportul Internațional Cahul ',
                          'lat': '45.844174',
                          'lon': '28.263148',
                          'address': '',
                          'qr': ''},
                         {'name': 'Troițcoe-Visoceanskoe',
                          'lat': '46.5037478',
                          'lon': '29.0399966',
                          'address': '',
                          'qr': ''},
                         {'name': 'Săiți-Lesnoe ',
                          'lat': '46.4712872',
                          'lon': '29.3989602',
                          'address': '',
                          'qr': ''},
                         {'name': 'Palanca - Maiki-Udobnoe ',
                          'lat': '46.413607',
                          'lon': '30.1607361',
                          'address': '',
                          'qr': ''},
                         {'name': 'Tudora-Starokazacie',
                          'lat': '46.3865733',
                          'lon': '30.0887191',
                          'address': '',
                          'qr': ''},
                         {'name': 'Caplani-Crutoiarovca ',
                          'lat': '46.3707702',
                          'lon': '29.8436202',
                          'address': '',
                          'qr': ''},
                         {'name': 'Iserlia-Petrovka ',
                          'lat': '46.4594727',
                          'lon': '28.9670505',
                          'address': '',
                          'qr': ''},
                         {'name': 'Volontir-Faraonovka ',
                          'lat': '46.3544235',
                          'lon': '29.6150709',
                          'address': '',
                          'qr': ''},
                         {'name': 'Copceac-Alexandrovka ',
                          'lat': '45.8914807',
                          'lon': '28.7613885',
                          'address': '',
                          'qr': ''},
                         {'name': 'Ucrainca-Lesnoe ',
                          'lat': '46.444573',
                          'lon': '29.3054686',
                          'address': '',
                          'qr': ''},
                         {'name': 'Direcţia regională NORD',
                          'lat': '48.1769039',
                          'lon': '27.2956181',
                          'address': '',
                          'qr': ''},
                         {'name': 'Direcția regionala Vest',
                          'lat': '47.197557',
                          'lon': '27.7887154',
                          'address': '',
                          'qr': ''},
                         {'name': 'Centrul de Excelență în Securitatea Frontierei',
                          'lat': '47.1977465',
                          'lon': '27.7889085',
                          'address': '',
                          'qr': ''},
                         {'name': 'Inspectoratul General al Poliției de Frontieră',
                          'lat': '47.045417',
                          'lon': '28.8298523',
                          'address': '',
                          'qr': ''},
                         {'name': 'Aeroportul Internațional Chișinău',
                          'lat': '46.9354074',
                          'lon': '28.9356709',
                          'address': '',
                          'qr': ''},
                         {'name': 'Direcția regională Sud',
                          'lat': '45.9063749',
                          'lon': '28.1899738',
                          'address': '',
                          'qr': ''},
                         {'name': 'Direcția regională Est',
                          'lat': '46.5168232',
                          'lon': '29.6579361',
                          'address': '',
                          'qr': ''},
                         {'name': 'Cobasna-Slobodka',
                          'lat': '47.7981987',
                          'lon': '29.219579',
                          'address': '',
                          'qr': ''},
                         {'name': 'Novosaviţcaia-Kuciurgan ',
                          'lat': '46.7365004',
                          'lon': '29.9640239',
                          'address': '',
                          'qr': ''},
                         {'name': 'Hristovaia-Bolgan ',
                          'lat': '48.1335269',
                          'lon': '28.7393052',
                          'address': '',
                          'qr': ''},
                         {'name': 'Goianul Nou-Platonovo ',
                          'lat': '47.4036996',
                          'lon': '29.3290972',
                          'address': '',
                          'qr': ''},
                         {'name': 'Pervomaisc-Kuciurgan ',
                          'lat': '46.7360761',
                          'lon': '29.9782355',
                          'address': '',
                          'qr': ''},
                         {'name': 'Hruşca-Velikaia Kosniţa ',
                          'lat': '48.1272942',
                          'lon': '28.4992733',
                          'address': '',
                          'qr': ''},
                         {'name': 'Broşteni-Timkovo ',
                          'lat': '47.8794374',
                          'lon': '29.2727495',
                          'address': '',
                          'qr': ''},
                         {'name': 'Vadul Turcului-Şerşenţî ',
                          'lat': '47.9626059',
                          'lon': '28.9957841',
                          'address': '',
                          'qr': ''},
                         {'name': 'Vărăncău-Stanislavka ',
                          'lat': '47.7046992',
                          'lon': '29.2167076',
                          'address': '',
                          'qr': ''},
                         {'name': 'Colosova-Iosipovka ',
                          'lat': '47.3447818',
                          'lon': '29.5800375',
                          'address': '',
                          'qr': ''},
                         {'name': 'Blijnii Hutor-Slaveanoserbka',
                          'lat': '46.9233343',
                          'lon': '29.6827473',
                          'address': '',
                          'qr': ''},
                         {'name': 'Nezavertailovca-Gradinţî ',
                          'lat': '46.5857238',
                          'lon': '29.9513078',
                          'address': '',
                          'qr': ''},
                         {'name': 'Valea Adîncă-Zagnitkovo',
                          'lat': '48.0211052',
                          'lon': '28.8608169',
                          'address': '',
                          'qr': ''},
                         {'name': 'Cobasna-Domniţa ',
                          'lat': '47.8022608',
                          'lon': '29.2153252',
                          'address': '',
                          'qr': ''},
                         {'name': 'Ţîbuleuca-Ţehanovka ',
                          'lat': '47.458269',
                          'lon': '29.1908568',
                          'address': '',
                          'qr': ''},
                         {'name': 'Dubău-Dubovo ',
                          'lat': '47.4336892',
                          'lon': '29.2707431',
                          'address': '',
                          'qr': ''},
                         {'name': 'Mociarovca-Pavlovka ',
                          'lat': '47.2503971',
                          'lon': '29.5521283',
                          'address': '',
                          'qr': ''},
                         {'name': 'Tiraspol-Grebeniki ',
                          'lat': '46.8633143',
                          'lon': '29.7473824',
                          'address': '',
                          'qr': ''},
                         {'name': 'Frunză-Rozalovka ',
                          'lat': '46.8334792',
                          'lon': '29.8947504',
                          'address': '',
                          'qr': ''},
                         {'name': 'Ocniţa-Grabarivka ',
                          'lat': '48.1541551',
                          'lon': '28.6347156',
                          'address': '',
                          'qr': ''},
                         {'name': 'Mălăieşti-Velikopolskoe ',
                          'lat': '46.9581434',
                          'lon': '29.5568348',
                          'address': '',
                          'qr': ''},
                         {'name': 'Rotari-Studeonoe ',
                          'lat': '48.108809',
                          'lon': '28.853669',
                          'address': '',
                          'qr': ''},
                         {'name': 'Jura-Fedoseevka ',
                          'lat': '47.5269221',
                          'lon': '29.1377755',
                          'address': '',
                          'qr': ''},
                         {'name': 'Plopi-Crutîe ',
                          'lat': '47.9554918',
                          'lon': '29.1867431',
                          'address': '',
                          'qr': ''},
                         {'name': 'Vadul Turcului-Alexeevka ',
                          'lat': '47.9782057',
                          'lon': '28.959658',
                          'address': '',
                          'qr': ''},
                         {'name': 'Direcția regională Centru',
                          'lat': '47.0447627',
                          'lon': '28.8283074',
                          'address': '',
                          'qr': ''},
                         {'name': 'Mirnoe-Tabaki',
                          'lat': '45.7365967',
                          'lon': '28.581513',
                          'address': '',
                          'qr': ''},
                         {'name': 'PTF Criva - Mamaliga',
                          'lat': '48.2633119',
                          'lon': '26.6273397',
                          'address': '',
                          'qr': ''},
                         {'name': 'Basarabeasca - Serpniovo-1',
                          'lat': '46.3187046',
                          'lon': '28.9754094',
                          'address': '',
                          'qr': ''},
                         {'name': 'Copciac-Cervonoarmeiskoe ',
                          'lat': '45.817684',
                          'lon': '28.6972739',
                          'address': '',
                          'qr': ''}]
