import { combineReducers } from 'redux';
import balance from './balance/balanceReducer';
import critcalls from './critcalls/critcallsReducer';
import managers from './managers/managersReducer';
import calls from './calls/callsReducer';

const rootReducer = combineReducers({
    balance,
    critcalls,
    managers,
    calls,
});
export default rootReducer;
