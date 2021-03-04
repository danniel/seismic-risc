import React from 'react';
import { Trans } from '@lingui/macro';
import Layout from '../components/Layout';

const About = () => {
  return (
    <Layout>
      <div className="page">
        <h1>
          <Trans>Despre proiect</Trans>
        </h1>
      </div>
    </Layout>
  );
};

export default About;
