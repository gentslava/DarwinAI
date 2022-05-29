import React from 'react';
import logo from 'assets/images/logo.png';

const Logo = () => <img src={logo} alt='Logo' />;
export default React.memo(Logo);
