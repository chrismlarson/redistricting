from unittest import TestCase
import shapely.wkt
from geographyHelper import shapelyGeometryToGeoJSON, doesPolygonContainTheOther


class TestDoesPolygonContainTheOther(TestCase):

    def test_doesPolygonContainTheOther_NearEachOther(self):
        aShape = shapely.wkt.loads(
            'POLYGON ((-83.70833500000001 44.560671, -83.708504 44.56067, -83.70878399999999 44.560668, -83.710134 44.560663, -83.71058499999999 44.560662, -83.71102500000001 44.560659, -83.71234699999999 44.560651, -83.712788 44.560649, -83.713584 44.560632, -83.714253 44.560626, -83.714562 44.560629, -83.714793 44.560627, -83.715045 44.560608, -83.715193 44.560589, -83.715282 44.560572, -83.715402 44.560534, -83.71544799999999 44.56052, -83.71557300000001 44.560466, -83.71567899999999 44.56041, -83.71587700000001 44.560287, -83.71602 44.560183, -83.716156 44.560074, -83.716373 44.55992, -83.716489 44.559848, -83.71665299999999 44.55977, -83.71677 44.559725, -83.716847 44.559702, -83.716965 44.559686, -83.717069 44.559686, -83.717134 44.559691, -83.71731 44.559719, -83.717343 44.559731, -83.717382 44.559745, -83.717426 44.559759, -83.717727 44.559892, -83.7179 44.559975, -83.718228 44.560144, -83.71834200000001 44.560196, -83.718535 44.560266, -83.71872500000001 44.560327, -83.71911 44.56043, -83.719296 44.560472, -83.719589 44.560517, -83.719928 44.560554, -83.72021599999999 44.560576, -83.72050400000001 44.560592, -83.72086 44.560605, -83.721216 44.560613, -83.721672 44.560617, -83.72288399999999 44.560609, -83.72304 44.560609, -83.724469 44.560608, -83.725508 44.56059, -83.726123 44.561763, -83.72618300000001 44.561893, -83.726212 44.561954, -83.726294 44.562173, -83.726377 44.56244, -83.726409 44.562574, -83.726434 44.562716, -83.726465 44.563003, -83.72648 44.563206, -83.72650400000001 44.563814, -83.726533 44.564931, -83.72654199999999 44.565851, -83.726557 44.566255, -83.726569 44.566562, -83.726586 44.566812, -83.726629 44.567208, -83.726736 44.56771, -83.726782 44.568012, -83.726788 44.568036, -83.726933 44.568547, -83.72704299999999 44.568879, -83.727082 44.568983, -83.727198 44.569293, -83.72709500000001 44.56932, -83.727041 44.569331, -83.72692000000001 44.569357, -83.72678500000001 44.569397, -83.72669999999999 44.569431, -83.72666700000001 44.569454, -83.726634 44.56949, -83.726617 44.569524, -83.726592 44.569577, -83.726574 44.569679, -83.72659 44.569913, -83.726602 44.570484, -83.726601 44.570895, -83.72657700000001 44.572098, -83.726574 44.5727, -83.726597 44.573911, -83.72659899999999 44.574363, -83.7266 44.574385, -83.726573 44.575218, -83.72654900000001 44.576469, -83.726552 44.576598, -83.726575 44.576782, -83.72657700000001 44.576911, -83.72654900000001 44.577209, -83.726535 44.577426, -83.72653800000001 44.577588, -83.72656499999999 44.577912, -83.726568 44.578074, -83.726563 44.578314, -83.726637 44.578517, -83.726625 44.578621, -83.72657700000001 44.578701, -83.72649199999999 44.578874, -83.72641900000001 44.578973, -83.72633999999999 44.579103, -83.72622 44.579271, -83.725773 44.579926, -83.725449 44.580441, -83.724637 44.581246, -83.72451 44.581443, -83.724265 44.581892, -83.724199 44.581992, -83.724054 44.582188, -83.723994 44.58229, -83.723972 44.582342, -83.72394799999999 44.58245, -83.72394199999999 44.582537, -83.723944 44.582641, -83.723932 44.582691, -83.723888 44.58279, -83.723859 44.582838, -83.723797 44.582923, -83.723691 44.583036, -83.723612 44.583108, -83.723591 44.583134, -83.723578 44.583163, -83.723575 44.583203, -83.723586 44.583234, -83.723596 44.583251, -83.723634 44.583283, -83.72369999999999 44.583325, -83.723782 44.583365, -83.72381300000001 44.583391, -83.723843 44.583457, -83.723851 44.5835, -83.72385 44.583543, -83.723838 44.583609, -83.72381 44.583679, -83.723767 44.583747, -83.723705 44.583812, -83.723612 44.583883, -83.723563 44.583913, -83.723455 44.583963, -83.72339599999999 44.583982, -83.723282 44.584006, -83.72322800000001 44.584012, -83.723195 44.584012, -83.72300199999999 44.583991, -83.722818 44.583958, -83.722661 44.583945, -83.722598 44.583944, -83.72253600000001 44.583949, -83.72243 44.583975, -83.72236700000001 44.583997, -83.722307 44.584024, -83.72224300000001 44.584061, -83.722184 44.584103, -83.722086 44.584192, -83.72204600000001 44.584237, -83.722015 44.584288, -83.721979 44.584397, -83.721968 44.584485, -83.721974 44.584583, -83.721988 44.584648, -83.722013 44.584713, -83.722049 44.584776, -83.72222499999999 44.585049, -83.722279 44.585199, -83.72236599999999 44.585486, -83.722414 44.585665, -83.722426 44.585728, -83.722466 44.585927, -83.72252400000001 44.586271, -83.722559 44.586443, -83.72265 44.5868, -83.722656 44.586871, -83.722652 44.586923, -83.72261899999999 44.58704, -83.722587 44.587104, -83.722521 44.587214, -83.722416 44.587351, -83.722241 44.587549, -83.72209599999999 44.587695, -83.72193799999999 44.587844, -83.721825 44.587939, -83.721706 44.58803, -83.72144299999999 44.588201, -83.721346 44.58827, -83.721307 44.588309, -83.721284 44.588344, -83.721267 44.588382, -83.721251 44.58846, -83.721253 44.58851, -83.72127399999999 44.588587, -83.721357 44.58872, -83.72138200000001 44.588771, -83.7214 44.588822, -83.721406 44.588867, -83.721405 44.588911, -83.72139 44.588964, -83.72133700000001 44.589067, -83.72121199999999 44.589351, -83.721148 44.58946, -83.721109 44.589512, -83.721014 44.58961, -83.720983 44.589636, -83.72096000000001 44.589656, -83.72087000000001 44.58972, -83.720767 44.589776, -83.72069399999999 44.589809, -83.720539 44.58987, -83.72037400000001 44.589963, -83.720259 44.590041, -83.720151 44.590126, -83.72008700000001 44.590186, -83.720022 44.590257, -83.719965 44.590333, -83.719917 44.590411, -83.719859 44.590533, -83.71984 44.590597, -83.719831 44.590667, -83.71983 44.590672, -83.71983 44.590737, -83.719843 44.590818, -83.71990599999999 44.591028, -83.719956 44.591175, -83.719983 44.591273, -83.72001 44.591462, -83.720004 44.59162, -83.719994 44.591683, -83.71997399999999 44.591744, -83.71995200000001 44.591785, -83.719894 44.591862, -83.719875 44.59188, -83.71961400000001 44.592078, -83.719493 44.592179, -83.71938 44.592284, -83.719195 44.592482, -83.719043 44.592661, -83.718975 44.592758, -83.71885 44.592956, -83.718512 44.593464, -83.71844299999999 44.593557, -83.718215 44.593807, -83.718146 44.593888, -83.718084 44.593971, -83.71801499999999 44.594097, -83.717867 44.594445, -83.717822 44.594528, -83.717726 44.594673, -83.717708 44.594693, -83.717654 44.594759, -83.717529 44.594892, -83.71727 44.595128, -83.71717700000001 44.595227, -83.717101 44.595324, -83.71707000000001 44.595389, -83.717033 44.595504, -83.71697399999999 44.595858, -83.716887 44.596028, -83.71563399999999 44.594929, -83.71425499999999 44.593968, -83.71414900000001 44.593925, -83.71373199999999 44.593756, -83.713009 44.593262, -83.71271 44.592866, -83.71132299999999 44.591534, -83.710786 44.590625, -83.710696 44.589602, -83.71102 44.588624, -83.71093 44.5876, -83.710339 44.587271, -83.70968000000001 44.586641, -83.70899199999999 44.586265, -83.70887 44.586236, -83.705502 44.585441, -83.705462 44.585427, -83.705326 44.585391, -83.704977 44.585315, -83.704897 44.585294, -83.704841 44.58528, -83.70402199999999 44.585037, -83.70311 44.584759, -83.703024 44.584733, -83.702629 44.584619, -83.70251399999999 44.584583, -83.70236 44.584536, -83.70222200000001 44.5845, -83.70200699999999 44.58446, -83.701823 44.584442, -83.701747 44.584439, -83.701589 44.584447, -83.701505 44.584459, -83.70141 44.584488, -83.701227 44.584528, -83.70111900000001 44.584513, -83.70101099999999 44.584472, -83.700918 44.584384, -83.700654 44.584188, -83.70017199999999 44.583859, -83.700002 44.583726, -83.699844 44.58358, -83.699691 44.583359, -83.69962200000001 44.583259, -83.699506 44.583111, -83.699387 44.582855, -83.699326 44.582784, -83.699072 44.582632, -83.69855699999999 44.582297, -83.69825400000001 44.582083, -83.698199 44.581932, -83.69818600000001 44.581743, -83.69812899999999 44.58164, -83.69798400000001 44.58155, -83.697734 44.581531, -83.69735799999999 44.581565, -83.697064 44.581612, -83.69584999999999 44.581913, -83.69478599999999 44.582202, -83.694649 44.582229, -83.69452699999999 44.582244, -83.694424 44.582239, -83.69426300000001 44.582177, -83.694068 44.582139, -83.69358099999999 44.582076, -83.69336 44.582013, -83.693212 44.581957, -83.693082 44.581818, -83.693005 44.581695, -83.692925 44.581623, -83.692792 44.581585, -83.69242199999999 44.581598, -83.69225900000001 44.5816, -83.692098 44.581551, -83.69156099999999 44.58115, -83.69120100000001 44.581037, -83.691182 44.581031, -83.69095799999999 44.580965, -83.690788 44.580962, -83.690566 44.581023, -83.690299 44.581134, -83.69007499999999 44.581236, -83.689654 44.581496, -83.689425 44.581725, -83.689241 44.581878, -83.689104 44.581947, -83.688954 44.581964, -83.68822900000001 44.581956, -83.68814399999999 44.581955, -83.68811700000001 44.581606, -83.688052 44.58099, -83.688067 44.580851, -83.688112 44.580719, -83.688187 44.580567, -83.688233 44.580494, -83.688393 44.580281, -83.688613 44.580043, -83.688648 44.580008, -83.68893199999999 44.579735, -83.688984 44.579671, -83.689072 44.579538, -83.68917500000001 44.579329, -83.689235 44.579164, -83.689284 44.578972, -83.68934299999999 44.57866, -83.689419 44.578431, -83.68950700000001 44.578281, -83.68956300000001 44.578214, -83.689694 44.578088, -83.68987799999999 44.577955, -83.690073 44.577846, -83.69023 44.577774, -83.690451 44.577687, -83.69062700000001 44.577639, -83.69132399999999 44.577575, -83.69159500000001 44.57756, -83.692413 44.57754, -83.692881 44.577519, -83.693079 44.577497, -83.693333 44.577443, -83.693499 44.577384, -83.693652 44.57731, -83.693872 44.577187, -83.693943 44.577142, -83.69422400000001 44.57697, -83.694464 44.576841, -83.6947 44.576741, -83.694869 44.576682, -83.695046 44.576601, -83.695155 44.576533, -83.695234 44.576449, -83.695262 44.576403, -83.69528200000001 44.576309, -83.695278 44.576126, -83.695266 44.57604, -83.695182 44.575717, -83.695178 44.575702, -83.69505599999999 44.575328, -83.69502 44.575215, -83.69496599999999 44.574959, -83.69493199999999 44.5747, -83.69492200000001 44.574311, -83.694931 44.574174, -83.69493799999999 44.57412, -83.69496700000001 44.5739, -83.694997 44.573717, -83.69511 44.573516, -83.695401 44.573005, -83.695431 44.572907, -83.695458 44.572825, -83.69547900000001 44.572683, -83.695481 44.572662, -83.69549000000001 44.572603, -83.695494 44.572583, -83.69548899999999 44.572403, -83.695475 44.571863, -83.695471 44.571683, -83.695609 44.571649, -83.69592 44.571575, -83.695988 44.571488, -83.696077 44.571377, -83.69615 44.571419, -83.696192 44.571432, -83.69628 44.571443, -83.696652 44.571452, -83.696871 44.571498, -83.697101 44.571517, -83.697215 44.571547, -83.697362 44.571586, -83.697451 44.571599, -83.697819 44.571597, -83.698122 44.571552, -83.698306 44.571539, -83.698498 44.57155, -83.69852899999999 44.571569, -83.69855200000001 44.571596, -83.698565 44.571623, -83.698583 44.571657, -83.698617 44.571758, -83.698633 44.571986, -83.698667 44.57215, -83.698714 44.572276, -83.69879400000001 44.572466, -83.698825 44.572562, -83.69892900000001 44.57325, -83.698983 44.573478, -83.699073 44.573632, -83.699106 44.573689, -83.69924399999999 44.573862, -83.699332 44.573936, -83.69960500000001 44.574117, -83.699659 44.574166, -83.69967800000001 44.574196, -83.699716 44.574361, -83.69973299999999 44.574515, -83.69974999999999 44.574677, -83.699759 44.574756, -83.699816 44.574879, -83.699882 44.574967, -83.699974 44.575041, -83.70001499999999 44.575065, -83.700081 44.575104, -83.700163 44.575135, -83.700204 44.575151, -83.700377 44.575197, -83.70051100000001 44.575222, -83.70064499999999 44.575238, -83.701018 44.575238, -83.70115199999999 44.575252, -83.701452 44.575337, -83.701947 44.575416, -83.70217599999999 44.575483, -83.702195 44.575496, -83.702296 44.575496, -83.702434 44.575474, -83.702519 44.575444, -83.702545 44.575422, -83.702561 44.575391, -83.70257599999999 44.575323, -83.702564 44.575158, -83.702618 44.575068, -83.70267200000001 44.575016, -83.702749 44.574958, -83.702844 44.574903, -83.70292499999999 44.574873, -83.70300899999999 44.574848, -83.703412 44.574774, -83.703631 44.574722, -83.704318 44.574532, -83.704444 44.574491, -83.704521 44.574453, -83.70455200000001 44.574428, -83.704554 44.574424, -83.704594 44.57437, -83.70461299999999 44.57428, -83.704605 44.57414, -83.704571 44.574044, -83.704532 44.573984, -83.704494 44.573951, -83.704436 44.573915, -83.704352 44.573882, -83.704126 44.573852, -83.703991 44.573822, -83.70390999999999 44.573792, -83.70387599999999 44.573773, -83.70381399999999 44.573723, -83.70371900000001 44.573608, -83.703676 44.573479, -83.703665 44.57338, -83.703672 44.573317, -83.70371 44.573153, -83.703726 44.573054, -83.703722 44.572988, -83.703626 44.572804, -83.70343200000001 44.572519, -83.703407 44.572478, -83.703385 44.57245, -83.70336500000001 44.57242, -83.703295 44.572261, -83.703288 44.57213, -83.703299 44.572034, -83.70335300000001 44.571905, -83.703418 44.571817, -83.703479 44.57177, -83.703671 44.571677, -83.703763 44.5716, -83.703806 44.571543, -83.703828 44.571441, -83.703836 44.571315, -83.703828 44.571148, -83.703805 44.571052, -83.70374700000001 44.570925, -83.703671 44.570805, -83.703594 44.570725, -83.703467 44.570627, -83.703191 44.570454, -83.70292999999999 44.570314, -83.702738 44.570226, -83.70260399999999 44.570204, -83.70246899999999 44.570199, -83.702381 44.570215, -83.702258 44.570265, -83.702155 44.570328, -83.70207000000001 44.570407, -83.70202399999999 44.570465, -83.701848 44.570838, -83.701733 44.571019, -83.701622 44.571162, -83.701537 44.571242, -83.70146800000001 44.571285, -83.70143 44.571299, -83.70133800000001 44.571316, -83.701296 44.571329, -83.70107299999999 44.571467, -83.700958 44.571519, -83.70065099999999 44.571598, -83.700517 44.571615, -83.700425 44.571618, -83.70029 44.571593, -83.70021 44.57156, -83.700098 44.5715, -83.69996399999999 44.571409, -83.69969500000001 44.571185, -83.699315 44.570938, -83.699219 44.570867, -83.69916600000001 44.570814, -83.699123 44.570754, -83.699085 44.570658, -83.699054 44.570463, -83.699054 44.570299, -83.699146 44.569906, -83.69916499999999 44.569777, -83.699161 44.569745, -83.69911500000001 44.569651, -83.69910299999999 44.569585, -83.6991 44.569454, -83.699111 44.569289, -83.699145 44.569196, -83.69939100000001 44.568803, -83.699468 44.56865, -83.699479 44.568584, -83.69946299999999 44.56842, -83.699417 44.568255, -83.699444 44.568159, -83.699483 44.568098, -83.699532 44.568044, -83.699636 44.567978, -83.700215 44.567706, -83.70041500000001 44.567624, -83.700622 44.567552, -83.700948 44.567459, -83.70096700000001 44.567454, -83.701055 44.567434, -83.70114700000001 44.567426, -83.701194 44.567429, -83.701278 44.567453, -83.70131600000001 44.567473, -83.701382 44.567522, -83.70142800000001 44.567527, -83.701466 44.567514, -83.70147 44.567483, -83.701458 44.567448, -83.70137800000001 44.567363, -83.701362 44.567336, -83.70136599999999 44.567305, -83.701447 44.56722, -83.70160799999999 44.567102, -83.70170299999999 44.566992, -83.701803 44.566806, -83.70184500000001 44.566644, -83.701849 44.566512, -83.70183 44.566381, -83.701795 44.566252, -83.70173 44.566096, -83.701645 44.565942, -83.70158000000001 44.565854, -83.70147299999999 44.565747, -83.701373 44.565679, -83.70133800000001 44.565618, -83.701319 44.565552, -83.70130399999999 44.565421, -83.701311 44.565355, -83.701342 44.565259, -83.70134899999999 44.564963, -83.701345 44.564732, -83.70132599999999 44.564571, -83.70125299999999 44.564346, -83.70122600000001 44.564316, -83.70115699999999 44.564274, -83.70107299999999 44.564244, -83.700985 44.564225, -83.700846 44.56422, -83.700616 44.564225, -83.700532 44.56425, -83.700486 44.564288, -83.700478 44.564324, -83.700501 44.564343, -83.70063500000001 44.564384, -83.70067400000001 44.564401, -83.70069700000001 44.564431, -83.700712 44.564464, -83.700716 44.564497, -83.700701 44.564527, -83.700639 44.564579, -83.70055499999999 44.564603, -83.700396 44.564637, -83.70029 44.564661, -83.700164 44.564697, -83.700041 44.564749, -83.69997600000001 44.564793, -83.699949 44.564821, -83.699918 44.564883, -83.69991 44.564949, -83.699911 44.565051, -83.699899 44.565081, -83.699849 44.565133, -83.699707 44.565221, -83.69963799999999 44.565309, -83.699592 44.565569, -83.699539 44.565696, -83.69948100000001 44.565786, -83.699454 44.565811, -83.69937400000001 44.565847, -83.69929 44.565869, -83.699151 44.565891, -83.699071 44.565918, -83.698913 44.565987, -83.69881100000001 44.566037, -83.69875999999999 44.566064, -83.698618 44.566146, -83.698549 44.566192, -83.698438 44.566297, -83.698369 44.566385, -83.69833800000001 44.566445, -83.698319 44.566541, -83.69832 44.566587, -83.69828800000001 44.566596, -83.698194 44.566624, -83.69816299999999 44.566634, -83.698021 44.566672, -83.69794400000001 44.566664, -83.697906 44.566661, -83.697774 44.566599, -83.697681 44.56652, -83.697529 44.566479, -83.697323 44.566492, -83.69730800000001 44.566493, -83.697103 44.56653, -83.69755600000001 44.566215, -83.698801 44.565353, -83.698792 44.56521, -83.69877 44.564846, -83.698674 44.564686, -83.69875500000001 44.564638, -83.698825 44.564588, -83.698998 44.564469, -83.69927300000001 44.564294, -83.69927800000001 44.564291, -83.699355 44.564254, -83.699444 44.564219, -83.69945 44.564217, -83.69955 44.564186, -83.69961600000001 44.564168, -83.699652 44.56416, -83.69987399999999 44.564114, -83.700148 44.564076, -83.700265 44.56406, -83.700327 44.564054, -83.700485 44.564039, -83.700587 44.564021, -83.70062 44.564012, -83.700684 44.563996, -83.70083099999999 44.563944, -83.700881 44.563919, -83.700914 44.563894, -83.700968 44.563838, -83.700981 44.563815, -83.70100499999999 44.563744, -83.701018 44.563679, -83.70102199999999 44.563613, -83.70101200000001 44.56338, -83.701008 44.563353, -83.70098400000001 44.563179, -83.700975 44.563059, -83.70092699999999 44.562599, -83.700785 44.561219, -83.700738 44.56076, -83.702257 44.560739, -83.70554 44.560695, -83.70681500000001 44.560684, -83.70833500000001 44.560671), (-83.700243 44.570072, -83.700767 44.569981, -83.70140000000001 44.569872, -83.702336 44.569683, -83.702859 44.569579, -83.70312800000001 44.569537, -83.703551 44.569473, -83.703934 44.569401, -83.704202 44.569352, -83.70419800000001 44.569511, -83.704223 44.569688, -83.70424800000001 44.569853, -83.704292 44.570086, -83.70434400000001 44.570317, -83.70444500000001 44.570678, -83.704469 44.570761, -83.70452400000001 44.570877, -83.70455800000001 44.570927, -83.704604 44.570971, -83.70461899999999 44.570988, -83.704685 44.571013, -83.70476499999999 44.571028, -83.704781 44.571028, -83.70490599999999 44.571033, -83.705354 44.571035, -83.705546 44.571037, -83.70555299999999 44.570696, -83.70556500000001 44.570161, -83.705564 44.569673, -83.705564 44.569332, -83.705572 44.568762, -83.70559299999999 44.567373, -83.705584 44.567054, -83.70556999999999 44.566485, -83.705292 44.566483, -83.70446 44.566478, -83.704183 44.566477, -83.703906 44.566479, -83.703078 44.566486, -83.70280200000001 44.566489, -83.70284700000001 44.566633, -83.70286 44.56669, -83.702883 44.566788, -83.702911 44.566944, -83.70293599999999 44.567195, -83.702912 44.567309, -83.70290199999999 44.567363, -83.702856 44.567511, -83.702687 44.567573, -83.702111 44.567847, -83.701852 44.567971, -83.70154599999999 44.568112, -83.701014 44.568347, -83.70071 44.568495, -83.700647 44.568529, -83.700591 44.568568, -83.700542 44.568613, -83.70049899999999 44.568663, -83.700462 44.568715, -83.70042599999999 44.568783, -83.700334 44.569051, -83.700299 44.569177, -83.700281 44.569257, -83.700272 44.569304, -83.70025200000001 44.569431, -83.70023999999999 44.569553, -83.700233 44.569798, -83.700238 44.570031, -83.700243 44.570072), (-83.707122 44.567016, -83.707151 44.56706, -83.707247 44.567145, -83.707275 44.567162, -83.70731000000001 44.567173, -83.707447 44.567186, -83.707486 44.56719, -83.707829 44.567188, -83.708614 44.56717, -83.708687 44.567169, -83.70883600000001 44.567143, -83.70891399999999 44.567118, -83.708984 44.567074, -83.70907200000001 44.567, -83.709197 44.566869, -83.709264 44.566784, -83.709378 44.566607, -83.70945 44.566468, -83.709476 44.566397, -83.709489 44.566335, -83.709509 44.566167, -83.70950999999999 44.566009, -83.709514 44.565743, -83.709506 44.565466, -83.709479 44.564912, -83.709451 44.564044, -83.709423 44.562884, -83.709425 44.562503, -83.709411 44.562313, -83.709408 44.562298, -83.709395 44.562219, -83.709356 44.562086, -83.70928600000001 44.562024, -83.709226 44.561995, -83.70916800000001 44.561977, -83.709041 44.561963, -83.708372 44.561983, -83.70808700000001 44.561985, -83.707235 44.561994, -83.706951 44.561998, -83.70698400000001 44.562501, -83.707004 44.563, -83.707038 44.563849, -83.70708500000001 44.565402, -83.70711 44.566012, -83.707138 44.566649, -83.707122 44.567016), (-83.69789 44.572783, -83.697845 44.572779, -83.69753 44.57274, -83.69747099999999 44.572733, -83.69743699999999 44.572729, -83.697304 44.572717, -83.69690799999999 44.572678, -83.69645 44.572645, -83.69643600000001 44.572644, -83.696152 44.572629, -83.696089 44.572625, -83.696091 44.572852, -83.69609699999999 44.573533, -83.6961 44.573761, -83.69633899999999 44.57377, -83.69640099999999 44.573773, -83.697057 44.573792, -83.69729700000001 44.573799, -83.697475 44.573804, -83.69801 44.573819, -83.698189 44.573824, -83.698173 44.573717, -83.698162 44.573619, -83.69809600000001 44.573003, -83.698075 44.572798, -83.698038 44.572795, -83.69792700000001 44.572786, -83.69789 44.572783))')
        a = shapelyGeometryToGeoJSON(aShape)

        bShape = shapely.wkt.loads(
            'POLYGON ((-83.695752 44.570567, -83.695752 44.570516, -83.695752 44.570363, -83.695752 44.570312, -83.695752 44.570196, -83.695745 44.570176, -83.695616 44.569788, -83.69557399999999 44.569659, -83.69557500000001 44.569572, -83.695578 44.569465, -83.695612 44.569316, -83.695632 44.569232, -83.69568 44.569408, -83.69571500000001 44.569471, -83.69576499999999 44.569526, -83.69576600000001 44.569527, -83.695995 44.569688, -83.696099 44.569797, -83.696172 44.569918, -83.69622200000001 44.570113, -83.69624399999999 44.570331, -83.696253 44.570409, -83.69623 44.570607, -83.696218 44.570659, -83.696113 44.570657, -83.695798 44.570654, -83.695787 44.570654, -83.695752 44.570567))')
        b = shapelyGeometryToGeoJSON(bShape)

        result = doesPolygonContainTheOther(aShape, bShape)
        self.assertFalse(result)
