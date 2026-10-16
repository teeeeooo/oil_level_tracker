from dataclasses import replace
import pytest
from tests.diagnostics.s11_terminal_veto_quarantine import quarantine
from tests.unit.test_oil_phase_lifecycle import _node, _unknown, _resolve
from oil_tracker.adapters.vision.oil_phase_lifecycle import OilMaterialPhase
from oil_tracker.domain.enums import InitialObservationState


def fill_layers(veto=False, recovered=False):
    ys=[180.,150.,130.,95.,50.] + ([45.] if recovered else [])
    return tuple((_node(frame,'owner',y,direction=-1,progress=20.,
                       material_path=veto and frame==4,
                       material_conflict=.8 if veto and frame==4 else .0),_unknown(frame))
                 for frame,y in enumerate(ys))


def test_clean_fill_remains_byte_semantically_equal():
    layers=fill_layers(); original=_resolve(layers)
    with quarantine() as ops: result=_resolve(layers)
    assert original.__dict__==result.__dict__ and not ops
    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER


def test_vetoed_terminal_does_not_confirm_state_or_publish_current_oil():
    layers=fill_layers(veto=True); original=_resolve(layers)
    assert original.reasons[-1]=='FILL_SPAN_MATERIAL_VETO'
    with quarantine() as ops: result=_resolve(layers)
    assert len(ops)==1 and result.reasons[-1]=='HPA_TERMINAL_VETO_NOT_FULL'
    assert result.phases[-1] is not OilMaterialPhase.FILLED_BARRIER
    assert result.allowed_tracklet_ids[-1]==frozenset()
    assert result.path[-1].kind=='unknown'


def test_clean_later_terminal_is_evaluated_without_carrying_a_coordinate():
    layers=fill_layers(veto=True,recovered=True)
    with quarantine() as ops: result=_resolve(layers)
    assert result.allowed_tracklet_ids[4]==frozenset()
    assert result.phases[-1] is OilMaterialPhase.FILLED_BARRIER
    assert result.path[-1] is layers[-1][0] and result.path[-1].y==45.
    assert len(ops)==1


@pytest.mark.parametrize('initial',[InitialObservationState.FULL_NO_INTERFACE,InitialObservationState.EMPTY_NO_INTERFACE])
def test_confirmed_initial_state_not_opened(initial):
    layers=tuple((_unknown(i),) for i in range(9))
    original=_resolve(layers,confirmed_initial_state=initial)
    with quarantine() as ops: result=_resolve(layers,confirmed_initial_state=initial)
    assert result.__dict__==original.__dict__ and not ops
    assert all(node.kind=='unknown' for node in result.path)


def test_ambiguous_handoff_is_not_repaired_by_trial():
    layers=((_node(0,'a',180.,direction=-1,progress=20.),_unknown(0)),
            (_node(1,'b',160.,direction=-1,progress=20.),
             _node(1,'c',162.,direction=-1,progress=20.),_unknown(1)))
    original=_resolve(layers)
    with quarantine() as ops: result=_resolve(layers)
    assert original.__dict__==result.__dict__ and not ops
    assert result.ambiguous_frames==frozenset({1})
