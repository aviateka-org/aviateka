# Авиатека / Aviateka — журнал изменений / changelog

Номер версии MAJOR.MINOR.PATCH. MINOR растёт, когда добавляются инструменты, типы аппаратов, разделы или инструменты MCP. PATCH — исправления данных без новых разделов. MAJOR — несовместимые изменения схемы данных или имён инструментов MCP. Каждая версия записывается в журнал с датой и списком изменений.

Version MAJOR.MINOR.PATCH. MINOR grows when tools, aircraft types, sections or MCP tools are added. PATCH means data fixes without new sections. MAJOR means breaking changes to the data schema or MCP tool names. Every version is logged with its date and changes.

## 0.15.1 — 2026-11-27

- Калькулятор висения сверен с замерами NASA серийных квадрокоптеров (Russell и др., 2016). Исправлено: прежняя подсказка «у малых винтов FM часто ниже 0,5» слишком пессимистична для обычных винтов дронов — NASA намерило у винтов 9–15 дюймов FM 0,58–0,72; ниже 0,5 бывает у винтов мельче. FM по умолчанию теперь 0,6 вместо 0,5. Добавлен параметр download — потеря тяги на корпус (по NASA 5–15 %); на странице — поле «Потеря тяги на корпус». Проверка на DJI Phantom 3 Advanced: с разбросом замеров NASA калькулятор даёт 19–29 мин висения, середина 24 мин; производитель заявляет до ~23 мин полёта. Два новых эталона: «Серийные квадрокоптеры в висении (NASA, 2016)» и «Сверка калькулятора висения на Phantom 3».

- The hover calculator is checked against NASA measurements of production quadcopters (Russell et al., 2016). Fixed: the earlier hint that small rotors often have FM below 0.5 was too pessimistic for ordinary drone propellers — NASA measured FM 0.58–0.72 for 9–15 in rotors; below 0.5 happens with smaller rotors. Default FM is now 0.6 instead of 0.5. New parameter download — thrust lost on the body (NASA: 5–15 %); a matching field on the page. Check on the DJI Phantom 3 Advanced: with the NASA spread the calculator gives 19–29 min of hover, 24 min in the middle; the maker claims up to ~23 min of flight. Two new benchmarks: production quadcopters in hover (NASA, 2016) and the Phantom 3 hover check.

## 0.15.0 — 2026-11-27

- Калькуляторы для ракет и входа в атмосферу. Стандартная атмосфера расширена с 20 до 86 км (атмосфера США 1976 года, ниже 32 км совпадает с международной): семь слоёв, сверены с таблицами на 20, 32, 50, 70 и 86 км. Высота по-прежнему геопотенциальная, как в таблицах МСА; для высоты над уровнем моря есть параметр geometric. Новые калькуляторы на странице и инструменты MCP (всего 23): «Ракета: прирост скорости» (rocket_delta_v — формула Циолковского, тяга к весу, время работы; сверено с учебным примером ERAU) и «Вход в атмосферу: нагрев носка» (entry_heating — формула Саттона и Грейвса, число Маха, скоростной напор, разброс по постоянной из разных источников). Подъёмная сила аэростата теперь считается и для стратостатов выше 20 км.

- Calculators for rockets and atmospheric entry. The standard atmosphere is extended from 20 to 86 km (US Standard Atmosphere 1976, equal to the international one below 32 km): seven layers, checked against tables at 20, 32, 50, 70 and 86 km. Altitude is still geopotential, as in ISA tables; a geometric parameter gives height above sea level. New page calculators and MCP tools (23 in total): «Rocket velocity gain» (rocket_delta_v — ideal rocket equation, thrust-to-weight, burn time; checked against an ERAU worked example) and «Entry: nose heating» (entry_heating — Sutton–Graves formula, Mach number, dynamic pressure, a range over the constant from different sources). Balloon lift now also works for stratospheric balloons above 20 km.

## 0.14.0 — 2026-11-27

- Квадрокоптеры. Лист «мультикоптер» и раньше считался покрытым, но в основном за счёт общих программ и программ для больших аппаратов с вертикальным взлётом; программ именно для малых дронов не было. Добавлены: FAST-UAV (облик дрона под задание, ISAE-SUPAERO), RotorPy и gym-pybullet-drones (тренажёры мультикоптера), PX4 (открытый автопилот с полётом в симуляции), PyBaMM (модель аккумулятора под нагрузкой) и база замеров малых винтов Университета Иллинойса. Цепочка «Квадрокоптер: от облика до полёта на автопилоте». Новый калькулятор «Винт: мощность висения» на странице и инструмент MCP rotor_hover (всего 21): тяга и мощность по теории импульса с коэффициентом качества винта, мощность от батареи и время висения. Проверка: совпадает с формулой в замкнутом виде до сотых ватта.

- Quadcopters. The multicopter leaf already counted as covered, but mainly thanks to general tools and tools for large VTOL aircraft; there were no tools for small drones as such. Added: FAST-UAV (drone sizing to a mission, ISAE-SUPAERO), RotorPy and gym-pybullet-drones (multirotor simulators), PX4 (open autopilot that also flies in simulation), PyBaMM (battery model under load) and the University of Illinois small-propeller measurements. Workflow «Quadcopter: from sizing to flying on an autopilot». New «Rotor hover power» calculator on the page and MCP tool rotor_hover (21 in total): thrust and power by momentum theory with the rotor figure of merit, battery power and hover time. Check: matches the closed-form formula to hundredths of a watt.

## 0.13.0 — 2026-11-27

- Последняя ветка классификатора. Три новых вида: гражданская ракета, аппарат для другой планеты, судно на воздушной подушке. Новые карточки: OpenRocket, openMotor, NASA CEA (открыт NASA, Apache-2.0), RocketCEA, RASAero II (бесплатный, код закрыт) и FLOTILLA (волновое сопротивление судна на подушке). RocketPy и Tudat отмечены для ракет, JSBSim (модель атмосферы Марса) и PlanetaryBalloon — для других планет. Три цепочки: модельная ракета, жидкостный двигатель, аппарат для другой планеты. Четыре пробела-окна: висение на реактивных струях, необычные схемы (ионный ветер, Магнус, FanWing), самолёт или вертолёт другой планеты, судно на воздушной подушке. Термины: запас устойчивости в калибрах, удельный импульс, гибкое ограждение. Итог прохода по классификатору: не покрыто 5 листьев из 34 вместо 15 — тепловой и привязной аэростаты, вингсьют, реактивный вертикальный взлёт и необычные схемы; под них открытых программ нет. Описание проекта обновлено: каталог теперь для летательных аппаратов всех видов.

- Last classifier branch. Three new types: civil rocket, craft for another planet, hovercraft. New cards: OpenRocket, openMotor, NASA CEA (opened by NASA, Apache-2.0), RocketCEA, RASAero II (free, closed source) and FLOTILLA (hovercraft wave resistance). RocketPy and Tudat tagged for rockets, JSBSim (Mars atmosphere model) and PlanetaryBalloon for other planets. Three workflows: model rocket, liquid engine, craft for another planet. Four window gaps: jet-borne hover, unusual layouts (ionic wind, Magnus, FanWing), aircraft or rotorcraft on another planet, hovercraft. Terms: stability margin in calibres, specific impulse, skirt. Result of the classifier pass: 5 of 34 leaves uncovered instead of 15 — hot-air and tethered balloons, wingsuit, jet VTOL and unusual layouts; there are no open tools for them. Project description updated: the catalog now covers flying craft of every kind.

## 0.12.0 — 2026-11-27

- Ветка сверхзвука, гиперзвука и входа в атмосферу. Два новых вида: сверхзвуковой и гиперзвуковой аппарат; вход в атмосферу. Восемь карточек: Eilmer (гиперзвук с химией, Квинсленд), SPARTA (разреженный газ, Sandia), Mutation++ (свойства горячего газа), hyStrath (гиперзвук в OpenFOAM), PATO (прогрев и унос теплозащиты, NASA), Tudat (траектория входа, TU Delft), PySAGAS и hypervehicle (форма гиперзвукового аппарата). SU2 (решатель NEMO), OpenVSP (волновое сопротивление) и OpenFOAM отмечены для новых видов. Три цепочки: сверхзвуковой самолёт, гиперзвуковой аппарат, вход в атмосферу. Пробел-окно: открытого расчёта звукового удара до земли нет. Термины: волновое сопротивление, абляция, число Кнудсена.

- Supersonic, hypersonic and entry branch. Two new types: supersonic and hypersonic vehicle; atmospheric entry. Eight cards: Eilmer (reacting hypersonics, Queensland), SPARTA (rarefied gas, Sandia), Mutation++ (hot-gas properties), hyStrath (hypersonics in OpenFOAM), PATO (heatshield heating and ablation, NASA), Tudat (entry trajectory, TU Delft), PySAGAS and hypervehicle (hypersonic vehicle shape). SU2 (NEMO solver), OpenVSP (wave drag) and OpenFOAM tagged for the new types. Three workflows: supersonic aircraft, hypersonic vehicle, atmospheric entry. Window gap: no open sonic boom propagation to the ground. Terms: wave drag, ablation, Knudsen number.

## 0.11.0 — 2026-11-27

- Ветка аппаратов легче воздуха. Новый калькулятор «Аэростат: подъёмная сила» на странице и инструмент MCP buoyancy (всего 20): гелий, водород с учётом чистоты, горячий воздух; полный и свободный подъём или нужный объём. Проверка: тепловой аэростат 2200 м³ при 100 °C внутри и 10 °C снаружи поднимает 0,301 кг на кубометр — как в независимом расчёте. Новый вид — дирижабль: карточка airship_simulation (мягкая оболочка в ROS и Gazebo), JSBSim (газовые ячейки и баллонеты) и OpenVSP отмечены для дирижаблей, цепочка «Дирижабль». Для стратосферных шаров — PlanetaryBalloon NASA (форма лепестковых шаров, программа 2007 года). Два пробела-окна: открытый расчёт облика дирижабля и модель привязного аэростата. Термины: баллонет, свободная подъёмная сила.
- Правило покрытия в классификаторе уточнено: лист, под чей тип нет ни одной программы, считается «не покрыто», а не «частично». Тепловой и привязной аэростаты пока не покрыты — открытых программ под них нет, есть только калькулятор и пробелы.

- Lighter-than-air branch. New «Balloon lift» calculator on the page and MCP tool buoyancy (20 in total): helium, hydrogen with purity, hot air; gross and net lift or the volume needed. Check: a 2,200 m³ hot-air balloon at 100 °C inside and 10 °C outside lifts 0.301 kg per cubic metre — as in an independent calculation. New type — airship: airship_simulation card (soft envelope in ROS and Gazebo), JSBSim (gas cells and ballonets) and OpenVSP tagged for airships, an airship workflow. For stratospheric balloons — NASA PlanetaryBalloon (lobed balloon shape, a 2007 program). Two window gaps: open airship sizing and a tethered aerostat model. Terms: ballonet, free lift.
- Classifier coverage rule refined: a leaf whose type has no tool counts as not covered rather than partial. Hot-air and tethered balloons stay uncovered for now — there are no open tools for them, only the calculator and the gaps.

## 0.10.0 — 2026-11-27

- Ветка винтокрылых. Три новых вида аппаратов: автожир, винтокрыл (вертолёт с крылом или толкающим винтом) и циклокоптер. Новые карточки: dynbem (винт от висения до авторотации и вихревого кольца), MBDyn (динамика лопастей и земной резонанс), NDARC (облик винтокрылых, только США) и RotaryWingSim (устойчивость автожира, код по запросу). JSBSim, preCICE и OpenFOAM отмечены для новых видов. Четыре цепочки: вертолёт, автожир, винтокрыл, циклокоптер. Три пробела-окна: открытая модель динамики автожира, открытый расчёт облика винтокрыла, быстрая модель циклоидального винта. Термины: авторотация, вихревое кольцо, земной резонанс. В классификаторе не покрыто теперь 11 листьев вместо 14.
- Исправлено: в записи 0.9.0 было «два новых термина», на деле новый один — редан, дельфинирование уже было в словаре. Сборка теперь ловит повторы id в цепочках, пробелах и словаре.

- Rotorcraft branch. Three new craft types: autogyro, compound helicopter and cyclocopter. New cards: dynbem (rotor from hover to autorotation and vortex ring state), MBDyn (blade dynamics and ground resonance), NDARC (rotorcraft sizing, U.S. only) and RotaryWingSim (autogyro stability, source on request). JSBSim, preCICE and OpenFOAM tagged for the new types. Four workflows: helicopter, autogyro, compound, cyclocopter. Three window gaps: open autogyro flight dynamics, open compound sizing, fast cycloidal rotor model. Terms: autorotation, vortex ring state, ground resonance. The classifier now has 11 uncovered leaves instead of 14.
- Fixed: the 0.9.0 entry said two new terms; only one (step) was new, porpoising was already in the glossary. The build now catches duplicate ids in workflows, gaps and the glossary.

## 0.9.0 — 2026-11-27

- Новый вид аппаратов — гидросамолёт и амфибия: цепочка от плавучести и остойчивости через разбег по воде и дельфинирование к посадке на воду и на волну. В каталоге DualSPHysics (метод частиц для удара о воду и брызг); для гидросамолётов отмечены JSBSim (упрощённая модель воды), OpenPlaning, FreeCAD Ship, OpenFOAM и Autowing. Новый пробел: открытого расчёта взлёта с воды целиком, вместе с аэродинамикой и дельфинированием, нет. Новый термин: редан. В классификаторе лист «гидросамолёт» перешёл из «не покрыто» в «частично».

- New craft type — seaplane and amphibian: a workflow from buoyancy and stability through the water run and porpoising to landing on calm water and waves. Added DualSPHysics (particle method for water impact and spray); JSBSim (simplified water model), OpenPlaning, FreeCAD Ship, OpenFOAM and Autowing are now tagged for seaplanes. New gap: no open whole-aircraft water take-off simulation with aerodynamics and porpoising. New term: step. In the classifier the seaplane leaf moved from not covered to partial.

## 0.8.0 — 2026-11-27

- Классификатор летательных аппаратов: 9 ветвей по тому, чем аппарат держится в воздухе, и 34 листа; для каждого листа каталог сам считает покрытие — инструменты, цепочки и итог «покрыто, частично, не покрыто». Сейчас покрыто 10, частично 9, не покрыто 15. Тут же сквозные признаки (взлёт, скорость, экипаж, двигатель, масса и правила, схема, назначение, среда) и деление аппаратов у ИКАО, Великобритании, FAA, EASA, по Воздушному кодексу РФ и у ИМО — со ссылками. Новый раздел страницы «Классы» и инструмент MCP get_classifier.
- Вне каталога теперь явно: боевые аппараты и ракетное оружие. Дальше каталог расширяется по непокрытым листьям по очереди: гидросамолёты, винтокрылые, дирижабли и аэростаты, сверхзвук и вход в атмосферу, ракеты, другие миры.

- Craft classifier: 9 branches by what holds a craft in the air and 34 leaves; for each leaf the catalog computes coverage itself — tools, workflows and a covered / partial / not covered verdict. Now 10 covered, 9 partial, 15 not covered. Also cross-cutting facets (take-off, speed, crew, propulsion, mass and rules, layout, purpose, environment) and how ICAO, the UK, FAA, EASA, the Russian Air Code and IMO split craft, with links. New page section 'Classes' and MCP tool get_classifier.
- Now explicitly out of scope: combat aircraft and missiles. Next, the catalog grows leaf by leaf through the uncovered ones: seaplanes, rotorcraft, airships and balloons, supersonic and entry, rockets, other worlds.

## 0.7.0 — 2026-11-27

- Новый калькулятор «Парашют: скорость снижения» на странице и в сервере MCP (parachute_descent): скорость спуска по массе, типу купола и его диаметру, разброс по коэффициенту сопротивления, энергия при посадке и с какой высоты это как прыжок; в обратную сторону — какой нужен купол для заданной скорости. Коэффициенты для восьми типов куполов — по Knacke и AFFDL-TR-78-151.
- Осторожно с исходными числами: коэффициенты плоского круглого купола и купола с удлинённой кромкой прочитаны с распознанного скана руководства Knacke — сверьте с оригиналом. Полусферический, конический и крестообразный купола не включены: их значения со скана надёжно не прочитались. Для них есть поле «свой CD0».

- New calculator 'Parachute descent rate' on the page and in the MCP server (parachute_descent): descent rate from mass, canopy type and diameter, its spread over the drag-coefficient range, landing energy and the equivalent jump height; in reverse, the canopy needed for a target rate. Coefficients for eight canopy types from Knacke and AFFDL-TR-78-151.
- Mind the inputs: the flat circular and extended-skirt coefficients come from an OCR scan of the Knacke manual — check the original. Hemispherical, conical and cross canopies are left out: their values could not be read reliably from the scan. Use the custom CD0 field for them.

## 0.6.0 — 2026-11-27

- Тканевые аппараты: пять новых типов — параплан, дельтаплан, парашют, змей и кайт, аэростат — и 21 новая карточка: OpenGlider, LEparagliding с lepg, SingleSkin, parabem, paraFEM, glidersim, наработки Avian для дельтапланов (HG-dev), Vortex Step Method, ASKITE, mem4py, KiteModels.jl, AWEbox, LAKSA, KiteModeler NASA, ChuteMaker, openchute, RocketPy, preCICE, Tawhiri, ASTRA и калькулятор газа CUSF.
- OpenVSP, XFLR5 и OpenFOAM отмечены для новых типов. Пять цепочек (параплан, дельтаплан, парашют, кайт, шар-зонд), пять пустых ниш (модель полёта дельтаплана, связка «ткань + стропы» для парафойла, раскрытие купола, вингсьют, оболочка теплового аэростата) и восемь терминов.
- Проверено не всё: условия лицензии ядра lep и дата и лицензия SingleSkin и HG-dev не сверены — страница автора lep, Codeberg и GitLab для проверки были закрыты. У openchute нет файла лицензии.

- Fabric craft: five new types — paraglider, hang glider, parachute, kite, balloon — and 21 new cards: OpenGlider, LEparagliding with lepg, SingleSkin, parabem, paraFEM, glidersim, Avian's hang-glider work (HG-dev), Vortex Step Method, ASKITE, mem4py, KiteModels.jl, AWEbox, LAKSA, NASA KiteModeler, ChuteMaker, openchute, RocketPy, preCICE, Tawhiri, ASTRA and the CUSF gas calculator.
- OpenVSP, XFLR5 and OpenFOAM are tagged for the new types. Five workflows (paraglider, hang glider, parachute, kite, sounding balloon), five gaps (hang-glider flight model, a fabric + lines loop for parafoils, canopy inflation, wingsuit, hot-air envelope) and eight terms.
- Not everything is verified: the licence of the lep core and the date and licence of SingleSkin and HG-dev are unchecked — the lep author page, Codeberg and GitLab were closed to our check. openchute has no licence file.

## 0.5.7 — 2026-11-27

- Версия поднимается сама: новая команда scripts/bump.py пишет запись в журнал и ставит номер во все файлы, а робот свежести вызывает её, когда меняются карточки. После слияния его правок новая версия сама уходит на PyPI и в каталог MCP.

- The version now bumps itself: the new scripts/bump.py command adds the changelog entry and sets the number in every file, and the freshness bot runs it when cards change. Once its changes are merged, the new version goes to PyPI and the MCP Registry by itself.

## 0.5.6 — 2026-11-27

- Автовыпуск: как только на основной ветке появляется новый номер версии, пакет сам уходит на PyPI, в каталог MCP и в выпуски GitHub с меткой. Ставить метку руками больше не нужно. Заодно на PyPI догоняет версия: там стояла 0.4.1, теперь будет текущая.

- Auto-release: as soon as a new version number lands on the main branch, the package goes to PyPI, the MCP Registry and a tagged GitHub release by itself. No manual tag is needed any more. PyPI also catches up: it had 0.4.1, now it gets the current version.

## 0.5.5 — 2026-11-26

- Исправлена ошибка версии 0.5.4: файлы Autowing на странице кафедры не свободные — все ссылки ведут на вход для сотрудников и студентов. Статус возвращён на «по запросу»; открыт без входа только учебный пример potentialVortex, к проектированию он не относится.

- Corrected a mistake in 0.5.4: the Autowing files on the chair page are not free — every link leads to a staff and student login. Status is back to on request; only the potentialVortex teaching case is public, and it is unrelated to design.

## 0.5.4 — 2026-11-26

- Autowing: программа, учебник, справка и описание математических моделей скачиваются со страницы кафедры в Ростоке свободно; статус сменён с «по запросу» на «бесплатно, без исходников». Условия лицензии на странице не указаны, за ними — к автору.

- Autowing: the program, tutorial, help file and description of the mathematical models can be downloaded freely from the Rostock chair page; status changed from on request to freeware. Licence terms are not stated there; ask the author.

## 0.5.3 — 2026-11-26

- Сайт подключён к Google Search Console: на страницах стоит метка владельца.

- The site is connected to Google Search Console: pages carry the owner verification tag.

## 0.5.2 — 2026-11-26

- Включён счётчик посещений GoatCounter (aviateka.goatcounter.com): без cookies, считает только просмотры страниц.

- The GoatCounter visit counter is on (aviateka.goatcounter.com): no cookies, counts page views only.

## 0.5.1 — 2026-11-26

- Первый проход робота свежести: новые даты коммитов у ArduPilot, FluidX3D и pyOptSparse, FluidX3D отмечен как живой.
- Исправлена ссылка на ветку форума boatdesign.net в карточке OpenPlaning.

- First freshness-bot pass: new commit dates for ArduPilot, FluidX3D and pyOptSparse; FluidX3D marked active.
- Fixed the boatdesign.net forum thread link on the OpenPlaning card.

## 0.5.0 — 2026-11-26

- Каждый инструмент получил свою обычную страницу (tools/…), есть общий список. Их видят поисковики и роботы ИИ, которые не запускают скрипты: раньше карточки каталога рисовались только скриптом и для них были невидимы.
- Карта сайта sitemap.xml, путеводители для ИИ llms.txt и llms-full.txt, описание набора данных для Google Dataset Search, превью ссылок в мессенджерах.
- Заготовки под счётчик посещений GoatCounter и проверку в Google Search Console: включаются одной строкой в data/meta.yaml. В README — значки версии и проверки.

- Every tool now has its own plain page (tools/…), plus a full list. Search engines and AI crawlers that do not run scripts can read them; before, the catalog cards were drawn only by a script and were invisible to them.
- A sitemap.xml, AI guides llms.txt and llms-full.txt, a dataset description for Google Dataset Search, link previews in messengers.
- Hooks for a GoatCounter visit counter and Google Search Console verification, switched on by one line in data/meta.yaml. Version and check badges in the README.

## 0.4.2 — 2026-11-26

- Сервер опубликован: пакет aviateka-mcp на PyPI и запись io.github.aviateka-org/aviateka в каталоге MCP (выпуск 0.4.1). Страница теперь предлагает ставить его одной командой uvx aviateka-mcp.

- The server is published: the aviateka-mcp package on PyPI and the io.github.aviateka-org/aviateka entry in the MCP Registry (release 0.4.1). The page now suggests installing it with one command, uvx aviateka-mcp.

## 0.4.1 — 2026-11-26

- Постоянный адрес проекта: организация aviateka-org на GitHub, репозиторий aviateka-org/aviateka, страница aviateka-org.github.io/aviateka, имя в каталоге MCP io.github.aviateka-org/aviateka.

- Permanent home: the aviateka-org organisation on GitHub, repository aviateka-org/aviateka, page aviateka-org.github.io/aviateka, MCP Registry name io.github.aviateka-org/aviateka.

## 0.4.0 — 2026-11-26

- Страница «О проекте» стала главной: что такое Авиатека, зачем она, как растёт (круг вклада), что внутри, как помочь, что нового. Числа и новости берутся из каталога сами.
- Каталог переехал по адресу catalog.html; название в шапке каталога ведёт на главную.

- An About page is now the front page: what Aviateka is, why, how it grows (the contribution loop), what is inside, how to help, what is new. Numbers and news come from the catalog automatically.
- The catalog moved to catalog.html; the name in its header links back to the front page.

## 0.3.0 — 2026-11-26

- Открытый проект: каталог разложен на файлы (одна карточка — один файл), появились схемы данных и проверка каждого изменения.
- Таблица сверки «кто чем считал и насколько совпало с опытом»; первые строки — Autowing и модель Ombor по диссертации 2023 года.
- Формы вклада без Git (инструмент, правка, свой расчёт, тема), раздел «Как помочь» и ссылка «Предложить правку» на каждой карточке.
- Инструменты MCP get_validation и how_to_contribute; сервер ставится пакетом aviateka-mcp.
- Робот раз в неделю обновляет даты коммитов, статусы и проверяет ссылки; выпуск по метке публикует пакет и сервер в каталоге MCP.
- Лицензии: код — MIT, данные — CC BY 4.0. Карточки внутри клетки карты теперь идут по алфавиту.

- Open project: the catalog is split into files (one card per file), with data schemas and a check on every change.
- Validation matrix "who computed what and how well it matched"; first rows are Autowing and Ombor's model from the 2023 thesis.
- Contribution forms without Git (tool, correction, calculation, topic), a Contribute section and a "Suggest a correction" link on every card.
- MCP tools get_validation and how_to_contribute; the server installs as the aviateka-mcp package.
- A weekly bot refreshes commit dates and statuses and checks links; a tagged release publishes the package and the MCP Registry entry.
- Licences: code MIT, data CC BY 4.0. Cards within a chart cell are now in alphabetical order.

## 0.2.2 — 2026-11-26

- Карточка Autowing: по спискам публикаций кафедры добавлены период активной работы (1997–2014, последняя статья 2019) и ссылка на бесплатный учебник автора с главой о динамике экраноплана.

- Autowing card: from the chair's publication lists, added the active period (1997–2014, last paper 2019) and the author's free textbook with a chapter on WIG dynamics.

## 0.2.1 — 2026-11-26

- Карточка Autowing уточнена по разбору: история метода (1992 → версия 2.4 в 1998 → 2019), нелинейный нестационарный метод, оговорка о точности по независимой сверке 2023 года, пять источников.

- Autowing card refined after a deep review: method history (1992 → v2.4 in 1998 → 2019), nonlinear unsteady method, accuracy caveat from an independent 2023 check, five sources.

## 0.2.0 — 2026-11-26

- Новые типы аппаратов: экраноплан и судно на подводных крыльях; новая дисциплина «Гидродинамика».
- 11 новых инструментов: Autowing, PUFFIn, Typhoon, MachUpHydro, DCFoil.jl, OpenPlaning, FreeCAD Ship, LEModeler, FASTSHIPS, симулятор Hydroptère, комплекс устойчивости экраноплана.
- У AVL, OpenVSP, flow5, XFOIL, NeuralFoil, OpenFOAM, SU2, OpenProp и ArduPilot добавлено применение к экранопланам и крыльям в воде.
- 2 цепочки (экраноплан, судно на крыльях), 3 ниши, 3 эталона, 9 терминов.
- Калькулятор кавитации; инструменты MCP get_changelog и cavitation.
- Журнал версий и правила нумерации в каталоге, на странице и в MCP.

- New craft types: WIG craft and hydrofoil craft; new discipline 'Hydrodynamics'.
- 11 new tools: Autowing, PUFFIn, Typhoon, MachUpHydro, DCFoil.jl, OpenPlaning, FreeCAD Ship, LEModeler, FASTSHIPS, Hydroptère simulator, WIG stability tool.
- AVL, OpenVSP, flow5, XFOIL, NeuralFoil, OpenFOAM, SU2, OpenProp and ArduPilot now tagged for WIG and hydrofoil use.
- 2 workflows (WIG, hydrofoil), 3 gaps, 3 benchmarks, 9 terms.
- Cavitation calculator; MCP tools get_changelog and cavitation.
- Version log and numbering rules in the catalog, page and MCP.

## 0.1.0 — 2026-11-26

- Первая версия: 54 инструмента, 12 цепочек, 5 ниш, 6 эталонов, 22 термина, кейс «Стриж».
- Страница с картой «дисциплина × точность» и MCP-сервер с 13 инструментами и 5 калькуляторами.

- First release: 54 tools, 12 workflows, 5 gaps, 6 benchmarks, 22 terms, the Strizh case.
- Page with a discipline × fidelity chart and an MCP server with 13 tools and 5 calculators.
