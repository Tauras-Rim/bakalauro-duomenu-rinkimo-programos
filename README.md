# Duomenų rinkimui sukurtos ir tyrime naudotos programos

Šioje repozitorijoje laikomos visos bakalauro metu sukurtos ir panaudotos programos bei jų trumpas paaiškinimas. Programos skirtos surinkti tinkamus Dependabot naudojančius bei nenaudojančius projektus naudojant GitHub REST API bei iš atrinktų projektų apskaičiuoti įvairius priklausomybių duomenis (jų kiekį, amžių ir panašiai). 

Programose, kurios naudoja GitHub REST API reikia nurodyti savo asmeninį Git žetoną (angl. token). Šios programos yra: dependabot_repo_getter, fork_checker, local_bot_checker, non_bot_repo_getter.

## Projektų surinkimo iš GitHub sistemos programos

### 1. dependabot_repo_getter

Suranda ir į tekstinį failą išsaugo projektus kurie naudoja Dependabot (jų pavadinimus ir savininkus), kurie randami naudojant GitHub REST API.

Programoje nustatomi dependabot.yml dydžio rėžiai, kurie padeda apeiti GitHub puslapių ribotumus ir rezultatų tekstinio failo pavadinimas.

### 2. non_bot_repo_getter

Suranda ir į tekstinį failą išsaugo projektus, kurie nenaudoja Dependabot ar kitų automatinių priklausomybių versijų atnaujinimo įrankių, (jų pavadinimus ir savininkus), kurie randami naudojant GitHub REST API.

Programoje nustatomi projektų sukūrimo datų laikotarpiai siekiant apeiti GitHub REST API puslapių ribotumus, tikrinamų automatinių priklausomybių atnaujinimo įrankių pavadinimai, maksimalus projektų kiekis grąžinamas iš GitHub REST API, rezultatų tekstinio failo pavadinimas. Taip pat galima nurodyti ir egzistuojančio rezultatų tekstinio failo pavadinimą jei programa paleidžiama daugiau nei vieną kartą (šiame faile laikomi projektai bus netikrinami kuriant GitHub REST API užklausą).

### 3. fork_checker

Patikrina, ar tekstiniame faile išsaugoti projektai (faile saugomi projektų savininkai ir pavadinimai) yra šakotiniai (angl. fork). Rezultatai išrašomi į terminalą.


### 4. repo_cloner

Skaitant tekstinį failą, kuriame nurodyti projektų savininkai ir pavadinimai (formatu savininkas/pavadinimas), atitinkami projektai klonuojami iš GitHub sistemos.

Programoje galima nustatyti projektų tekstinio failo pilną kelią bei aplanko, į kurį norima klonuoti visus gitHub sistemoje rastus projektus, pilną kelią.

### 5. local_bot_checker

Nustato, ar projektuose, kurie klonuoti į lokalų aplanką, yra repozitorijos pakeitimų sukurtų naudojant automatinius priklausomybės atnaujinimo įrankius. Ši programa naudojama kaip papildoma patikra projektams, po non_bot_repo_getter pargramos daromos patikros ir klonavimo į lokalų aplanką. Galutiniai rezultatai spausdinami į terminalą.

Programoje galima nustatyti skirtingų automatinių priklausomybių atnaujinimo įrankių, dėl kurių bus tikrinami projekto atnaujinimai, pavadinimus bei lokalaus aplanko, kuriame laikomi projektai, pilnas kelias.

## Projektų aktyvumo ir dydžio matavimo programos

### 1. activity_checker

Programa skirta patikrinti lokaliam aplanke esančių projektų aktyvumą (kiek mėnesių projektas turi bent po vieną git įkėlimą nuo 2023 metų sausio). 

Programoje nurodomas pilnas aplanko kelias ir galutinis kableliais atskirtų reikšmių failas, į kurį bus surašomi projekto aktyvumo rezultatai.

### 2. depenency_counter

Suranda visus projektus lokaliam aplanke ir apskaičiuoja jų priklausomybių kiekį bei bendrą visų projektų priklausomybių kiekį šiuo metu. Programa rezultatus surašo į kableliais atskirtų reikšmių failą.

Programoje galima nurodyti pilną kelią lokalaus aplanko, kuriame laikomi projektai bei kableliais atskirtų reikšmių rezultatų failo pavadinimą.

### 3. dependency_tracker

Analizuoja projekto projektinius (csproj) failus ir suskaičiuoja bendrą projekto naudojamų priklausomybių kiekį tam tikru metu. Galutiniai rezultatai išrašomi į kableliais atskirtų reikšmių failą.

Programai į parametrus paduodami pilnas kelias į lokaliai klonuotą projektą.

## Projektų priklausomybių amžiaus sekimo programos

### 1. libyear_tracker_normalized

Apskaičiuoja projekto visų priklausomybių vidutinį amžių tam tikru metu ir surašo atsakymus į kableliais atskirtų reikšmių failą.

Programoje galima nustatyti kableliais atskirtų reikšmių rezultatinių failų pavadinimus Dependabot naudojantiems ir nenaudojantiems projektams. Į programos parametrus paduodamas projekto, kurio vidutinį priklausomybės amžių norima išanalizuoti, pilnas kelias į lokalų aplanką.

### 2. libyear_tracker_standard

Apskaičiuoja projekto visų priklausomybių amžiaus visumą tam tikru metu ir surašo atsakymus į kableliais atskirtų reikšmių failą.

Programoje galima nustatyti kableliais atskirtų reikšmių rezultatinių failų pavadinimus Dependabot naudojantiems ir nenaudojantiems projektams. Į programos parametrus paduodamas projekto, kurio bendrą priklausomybių amžių norima išanalizuoti, pilnas kelias į lokalų aplanką.

## Papildomos programos

### 1. auto_repo_runner

Automatizuoja kitų programų vykdymą nurodytant lokalaus aplanko, kuriame laikomi projektai, pilną kelią bei naudojamos programos pilną kelią. Iš aplanko imami visi projektai ir su jais paleidžiama atitinkama programa.
