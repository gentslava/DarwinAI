import { UPDATE_CRITCALLS } from './types';

const initialState = {
    list: undefined,
};

const critcallsReducer = (state = initialState, action) => {
    switch (action.type) {
        case UPDATE_CRITCALLS:
            return { ...state, list: action.payload };
        default:
            return state;
    }
};
export default critcallsReducer;
