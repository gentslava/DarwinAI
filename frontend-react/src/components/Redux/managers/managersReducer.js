import { UPDATE_MANAGERS } from './types';

const initialState = {
    list: undefined,
};

const managersReducer = (state = initialState, action) => {
    switch (action.type) {
        case UPDATE_MANAGERS:
            return { ...state, list: action.payload };
        default:
            return state;
    }
};
export default managersReducer;
