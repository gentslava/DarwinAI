import React, { useEffect } from 'react';
import jsCookie from 'js-cookie';

const csrftoken = jsCookie.get('csrftoken');
const CSRFToken = ({ setCSRFMiddlewareToken }) => {
    useEffect(() => setCSRFMiddlewareToken(csrftoken));

    return <input type='hidden' name='csrfmiddlewaretoken' value={csrftoken} />;
};
export default React.memo(CSRFToken);
